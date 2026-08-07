import time
import re

from app.config.company_config import (
    get_enabled_assistant_modes,
    get_mode_fallback_message,
    get_mode_prompt_guide,
    load_company_config,
    resolve_assistant_mode,
)
from app.config.env_config import VECTOR_STORE
from app.llm.openai_provider import OpenAIProvider
from app.models.assistant_mode import AssistantMode
from app.services.answer_validation_service import validate_answer
from app.services.ingestion_service import get_index
from app.services.prompt_builder import build_rag_prompt
from app.services.usage_service import record_usage
from app.vector_store.supabase_store import SupabaseVectorStore


MIN_SOURCE_SCORE = 0.30

RUNTIME_DOCUMENT_NAME_PATTERN = re.compile(
    r"^[0-9a-fA-F]{32}_(.+)$"
)

SOURCE_METADATA_PATTERN = re.compile(
    r"\s*\[\[sources:\s*([^\]]+)\]\]\s*$",
    re.IGNORECASE,
)


def _display_source_name(
    filename: str | None,
) -> str | None:
    if not filename:
        return None

    match = RUNTIME_DOCUMENT_NAME_PATTERN.match(
        filename
    )

    if match:
        return match.group(1)

    return filename

def _answer_with_sources(
    *,
    question: str,
    mode: AssistantMode,
    sources: list[dict],
    request_started_at: float,
    retrieval_ms: float,
) -> dict:
    company = load_company_config()

    fallback_message = get_mode_fallback_message(
    company=company,
    mode=mode,
    )

    top_score = sources[0]["score"] if sources else None

    if top_score is None or top_score < MIN_SOURCE_SCORE:
        total_ms = (
            time.perf_counter() - request_started_at
        ) * 1000

        record_usage(
            {
                "question": question,
                "assistant_mode": mode.value,
                "vector_store": VECTOR_STORE,
                "refused": True,
                "reason": "weak_or_missing_sources",
                "retrieval_ms": retrieval_ms,
                "llm_ms": 0,
                "total_ms": total_ms,
                "source_count": len(sources),
                "top_score": top_score,
            }
        )

        return {
            "answer": fallback_message,
            "sources": [],
        }

    custom_prompt_guide = get_mode_prompt_guide(
    company=company,
    mode=mode,
    )

    prompt = build_rag_prompt(
    question=question,
    context_chunks=sources,
    company_name=company["company_name"],
    mode=mode,
    fallback_message=fallback_message,
    custom_guide=custom_prompt_guide,
    )

    provider = OpenAIProvider()

    llm_started_at = time.perf_counter()
    generation_result = provider.generate_with_usage(prompt)
    llm_ms = (
        time.perf_counter() - llm_started_at
    ) * 1000

    generated_answer, cited_source_ids = (
        _extract_answer_sources(
            generation_result["answer"]
        )
    )

    validation = validate_answer(
        question=question,
        answer=generated_answer,
        sources=sources,
        mode=mode,
    )

    total_ms = (
        time.perf_counter() - request_started_at
    ) * 1000

    record_usage(
        {
            "question": question,
            "assistant_mode": mode.value,
            "vector_store": VECTOR_STORE,
            "refused": not validation["valid"],
            "reason": validation["reason"],
            "retrieval_ms": retrieval_ms,
            "llm_ms": llm_ms,
            "total_ms": total_ms,
            "source_count": len(sources),
            "top_score": top_score,
            "usage": generation_result["usage"],
            "custom_prompt_guide_used": bool(custom_prompt_guide),
        }
    )

    safe_answer = validation["safe_answer"]

    is_fallback = (
        safe_answer.strip() == fallback_message.strip()
    )

    cited_source_id_set = set(cited_source_ids)

    supporting_sources = [
        source
        for source in sources
        if source["id"] in cited_source_id_set
    ]

    return {
        "answer": safe_answer,
        "sources": (
            supporting_sources
            if validation["valid"] and not is_fallback
            else []
        ),
    }


def _answer_from_local(
    question: str,
    mode: AssistantMode,
) -> dict:
    request_started_at = time.perf_counter()

    index = get_index(mode)

    if index is None:
        return _answer_with_sources(
        question=question,
        mode=mode,
        sources=[],
        request_started_at=request_started_at,
        retrieval_ms=0,
    )

    retriever = index.as_retriever(
        similarity_top_k=3,
    )

    retrieval_started_at = time.perf_counter()
    retrieved_nodes = retriever.retrieve(question)
    retrieval_ms = (
        time.perf_counter() - retrieval_started_at
    ) * 1000

    sources = []

    for node in retrieved_nodes:
        if (
            node.score is not None
            and node.score < MIN_SOURCE_SCORE
        ):
            continue

        sources.append(
            {
                "id": f"source_{len(sources) + 1}",
                "text": node.text,
                "score": node.score,
                "source": _display_source_name(
                    node.metadata.get("file_name")
                ),
            }
        )

    return _answer_with_sources(
        question=question,
        mode=mode,
        sources=sources,
        request_started_at=request_started_at,
        retrieval_ms=retrieval_ms,
    )


def _answer_from_supabase(
    question: str,
    mode: AssistantMode,
) -> dict:
    company = load_company_config()
    enabled_modes = get_enabled_assistant_modes(company)

    if len(enabled_modes) > 1:
        raise RuntimeError(
            "Supabase retrieval cannot serve multiple assistant modes "
            "until company and mode filtering has been configured."
        )

    request_started_at = time.perf_counter()

    store = SupabaseVectorStore()

    retrieval_started_at = time.perf_counter()

    matches = store.search_similar(
        question=question,
        match_count=3,
    )

    retrieval_ms = (
        time.perf_counter() - retrieval_started_at
    ) * 1000

    sources = []

    for match in matches:
        similarity = match.get("similarity")

        if (
            similarity is not None
            and similarity < MIN_SOURCE_SCORE
        ):
            continue

        metadata = match.get("metadata") or {}

        sources.append(
            {
                "id": f"source_{len(sources) + 1}",
                "text": match.get("content", ""),
                "score": similarity,
                "source": (
                    metadata.get("file_name")
                    or metadata.get("source")
                ),
            }
        )

    return _answer_with_sources(
        question=question,
        mode=mode,
        sources=sources,
        request_started_at=request_started_at,
        retrieval_ms=retrieval_ms,
    )


def answer_question(
    question: str,
    mode: AssistantMode | str | None = None,
) -> dict:
    resolved_mode = resolve_assistant_mode(mode)

    if VECTOR_STORE == "supabase":
        return _answer_from_supabase(
            question=question,
            mode=resolved_mode,
        )

    return _answer_from_local(
        question=question,
        mode=resolved_mode,
    )

def _extract_answer_sources(
    answer: str,
) -> tuple[str, list[str]]:
    match = SOURCE_METADATA_PATTERN.search(answer)

    if not match:
        return answer.strip(), []

    source_ids = [
        source_id.strip()
        for source_id in match.group(1).split(",")
        if source_id.strip()
    ]

    clean_answer = answer[:match.start()].strip()

    return clean_answer, source_ids