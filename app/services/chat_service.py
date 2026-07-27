import os
import time
from dotenv import load_dotenv

load_dotenv()

from llama_index.llms.openai import OpenAI

from app.llm.openai_provider import OpenAIProvider
from app.config import VECTOR_STORE, COMPANY_NAME, ENABLE_GREETING
from app.services.session_service import should_send_greeting
from app.services.answer_validation_service import validate_answer
from app.services.ingestion_service import get_index
from app.services.prompt_builder import build_rag_prompt
from app.services.usage_service import record_usage
from app.vector_store.supabase_store import SupabaseVectorStore
from app.constants import REFUSAL_TEXT

MIN_SOURCE_SCORE = 0.30


def _with_optional_greeting(answer: str) -> str:
    if ENABLE_GREETING and should_send_greeting():
        return (
            f"Hello, welcome to {COMPANY_NAME} chat. I'm your AI assistant.\n\n"
            + answer
        )

    return answer


def _answer_with_sources(
    question: str,
    sources: list[dict],
    retrieval_ms: float | None = None,
) -> dict:
    total_start = time.perf_counter()

    top_score = sources[0]["score"] if sources else None

    if top_score is None or top_score < MIN_SOURCE_SCORE:
        total_ms = (time.perf_counter() - total_start) * 1000

        record_usage(
            {
                "question": question,
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

        answer = REFUSAL_TEXT

        return {
            "answer": _with_optional_greeting(answer),
            "sources": sources,
        }

    prompt = build_rag_prompt(
        question=question,
        context_chunks=sources,
        company_name=COMPANY_NAME,
    )

    provider = OpenAIProvider()

    llm_start = time.perf_counter()
    generation_result = provider.generate_with_usage(prompt)
    llm_ms = (time.perf_counter() - llm_start) * 1000

    total_ms = (time.perf_counter() - total_start) * 1000

    validation = validate_answer(
        question=question,
        answer=generation_result["answer"],
        sources=sources,
    )

    record_usage(
        {
            "question": question,
            "vector_store": VECTOR_STORE,
            "refused": not validation["valid"],
            "reason": validation["reason"],
            "retrieval_ms": retrieval_ms,
            "llm_ms": llm_ms,
            "total_ms": total_ms,
            "source_count": len(sources),
            "top_score": top_score,
            "usage": generation_result["usage"],
        }
    )

    answer = validation["safe_answer"]

    return {
        "answer": _with_optional_greeting(answer),
        "sources": sources,
    }


def _answer_from_local(question: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    index = get_index()

    if index is None:
        return {
            "answer": "No documents ingested yet.",
            "sources": [],
        }

    query_engine = index.as_query_engine(
        llm=OpenAI(
            model="gpt-5-mini",
            api_key=api_key,
        ),
        similarity_top_k=3,
    )

    retrieval_start = time.perf_counter()
    retrieval_response = query_engine.query(question)
    retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

    sources = []
    for node in retrieval_response.source_nodes:
        if node.score is not None and node.score < MIN_SOURCE_SCORE:
            continue

        sources.append(
            {
                "id": f"source_{len(sources) + 1}",
                "text": node.text,
                "score": node.score,
                "source": node.metadata.get("file_name"),
            }
        )

    return _answer_with_sources(
        question=question,
        sources=sources,
        retrieval_ms=retrieval_ms,
    )


def _answer_from_supabase(question: str) -> dict:
    store = SupabaseVectorStore()

    retrieval_start = time.perf_counter()
    matches = store.search_similar(
        question=question,
        match_count=3,
    )
    retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

    sources = []
    for match in matches:
        similarity = match.get("similarity")

        if similarity is not None and similarity < MIN_SOURCE_SCORE:
            continue

        metadata = match.get("metadata") or {}

        sources.append(
            {
                "id": f"source_{len(sources) + 1}",
                "text": match.get("content", ""),
                "score": similarity,
                "source": metadata.get("file_name") or metadata.get("source"),
            }
        )

    return _answer_with_sources(
        question=question,
        sources=sources,
        retrieval_ms=retrieval_ms,
    )


def answer_question(question: str) -> dict:
    if VECTOR_STORE == "supabase":
        return _answer_from_supabase(question)

    return _answer_from_local(question)


def stream_answer_question(question: str):
    if VECTOR_STORE == "supabase":
        store = SupabaseVectorStore()

        matches = store.search_similar(
            question=question,
            match_count=3,
        )

        sources = []
        for match in matches:
            similarity = match.get("similarity")

            if similarity is not None and similarity < MIN_SOURCE_SCORE:
                continue

            metadata = match.get("metadata") or {}

            sources.append(
                {
                    "id": f"source_{len(sources) + 1}",
                    "text": match.get("content", ""),
                    "score": similarity,
                    "source": metadata.get("file_name") or metadata.get("source"),
                }
            )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")

        index = get_index()

        if index is None:
            yield "No documents ingested yet."
            return

        query_engine = index.as_query_engine(
            llm=OpenAI(
                model="gpt-5-mini",
                api_key=api_key,
            ),
            similarity_top_k=3,
        )

        retrieval_response = query_engine.query(question)

        sources = []
        for node in retrieval_response.source_nodes:
            if node.score is not None and node.score < MIN_SOURCE_SCORE:
                continue

            sources.append(
                {
                    "id": f"source_{len(sources) + 1}",
                    "text": node.text,
                    "score": node.score,
                    "source": node.metadata.get("file_name"),
                }
            )

    top_score = sources[0]["score"] if sources else None

    if top_score is None or top_score < MIN_SOURCE_SCORE:
        yield REFUSAL_TEXT
        return

    prompt = build_rag_prompt(
        question=question,
        context_chunks=sources,
        company_name=COMPANY_NAME,
    )

    provider = OpenAIProvider()

    for delta in provider.stream(prompt):
        yield delta