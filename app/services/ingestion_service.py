import os
import shutil
from pathlib import Path
from threading import RLock
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from app.config.company_config import (
    load_company_config,
    resolve_assistant_mode,
)
from app.config.env_config import VECTOR_STORE
from app.models.assistant_mode import AssistantMode
from app.vector_store.supabase_store import SupabaseVectorStore


AssistantModeInput = AssistantMode | str | None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_INDEX_ROOT = PROJECT_ROOT / "data" / "indexes"

EMBEDDING_MODEL = "text-embedding-3-small"

_local_indexes: dict[AssistantMode, VectorStoreIndex] = {}
_local_index_lock = RLock()


def _get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    return api_key


def _create_embedding_model() -> OpenAIEmbedding:
    return OpenAIEmbedding(
        model=EMBEDDING_MODEL,
        api_key=_get_api_key(),
    )


def _get_local_index_directory(
    mode: AssistantMode,
) -> Path:
    return LOCAL_INDEX_ROOT / mode.value


def _documents_to_nodes(
    documents: list[Any],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[Any]:
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    nodes = splitter.get_nodes_from_documents(documents)

    if not nodes:
        raise ValueError(
            "The supplied documents did not contain indexable content."
        )

    print(
        {
            "event": "documents_chunked",
            "documents_loaded": len(documents),
            "chunks_created": len(nodes),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "vector_store": VECTOR_STORE,
        }
    )

    return nodes


def _load_local_index_from_disk(
    mode: AssistantMode,
) -> VectorStoreIndex | None:
    persist_directory = _get_local_index_directory(mode)

    if (
        not persist_directory.is_dir()
        or not any(persist_directory.iterdir())
    ):
        return None

    try:
        storage_context = StorageContext.from_defaults(
            persist_dir=str(persist_directory),
        )

        index = load_index_from_storage(
            storage_context,
            embed_model=_create_embedding_model(),
        )
    except Exception as error:
        raise RuntimeError(
            "Could not load the persisted local index for "
            f"assistant mode '{mode.value}' from "
            f"'{persist_directory}'."
        ) from error

    print(
        {
            "event": "local_index_loaded",
            "assistant_mode": mode.value,
            "persist_directory": str(persist_directory),
        }
    )

    return index


def _persist_local_index(
    index: VectorStoreIndex,
    mode: AssistantMode,
) -> None:
    persist_directory = _get_local_index_directory(mode)

    persist_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        index.storage_context.persist(
            persist_dir=str(persist_directory),
        )
    except Exception as error:
        raise RuntimeError(
            "Could not persist the local index for "
            f"assistant mode '{mode.value}' to "
            f"'{persist_directory}'."
        ) from error

    print(
        {
            "event": "local_index_persisted",
            "assistant_mode": mode.value,
            "persist_directory": str(persist_directory),
        }
    )


def _get_cached_or_persisted_local_index(
    mode: AssistantMode,
) -> VectorStoreIndex | None:
    cached_index = _local_indexes.get(mode)

    if cached_index is not None:
        return cached_index

    persisted_index = _load_local_index_from_disk(mode)

    if persisted_index is not None:
        _local_indexes[mode] = persisted_index

    return persisted_index


def _build_local_index_from_nodes(
    nodes: list[Any],
    mode: AssistantMode,
    append: bool = False,
) -> None:
    with _local_index_lock:
        index = (
            _get_cached_or_persisted_local_index(mode)
            if append
            else None
        )

        if index is None:
            index = VectorStoreIndex(
                nodes,
                embed_model=_create_embedding_model(),
            )
        else:
            index.insert_nodes(nodes)

        _persist_local_index(
            index=index,
            mode=mode,
        )

        _local_indexes[mode] = index

    print(
        {
            "event": "local_index_updated",
            "assistant_mode": mode.value,
            "chunks_added": len(nodes),
            "append": append,
        }
    )


def _insert_nodes_into_supabase(
    nodes: list[Any],
    mode: AssistantMode,
) -> None:
    company = load_company_config()
    store = SupabaseVectorStore()

    for index, node in enumerate(nodes, start=1):
        metadata = dict(node.metadata)

        metadata["company_id"] = company["company_id"]
        metadata["assistant_mode"] = mode.value
        metadata["chunk_number"] = index

        inserted_id = store.insert_chunk(
            content=node.text,
            metadata=metadata,
        )

        print(
            {
                "event": "supabase_chunk_inserted",
                "inserted_id": inserted_id,
                "company_id": company["company_id"],
                "assistant_mode": mode.value,
                "source": metadata.get("file_name"),
                "chunk_number": index,
            }
        )


def _build_index_from_documents(
    documents: list[Any],
    mode: AssistantMode,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    append: bool = False,
) -> int:
    nodes = _documents_to_nodes(
        documents=documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if VECTOR_STORE == "supabase":
        _insert_nodes_into_supabase(
            nodes=nodes,
            mode=mode,
        )
    else:
        _build_local_index_from_nodes(
            nodes=nodes,
            mode=mode,
            append=append,
        )

    return len(documents)


def build_index_from_directory(
    path: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    append: bool = False,
    mode: AssistantModeInput = None,
) -> int:
    resolved_mode = resolve_assistant_mode(mode)

    documents = SimpleDirectoryReader(path).load_data()

    return _build_index_from_documents(
        documents=documents,
        mode=resolved_mode,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        append=append,
    )


def build_index_from_file(
    path: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    append: bool = False,
    mode: AssistantModeInput = None,
) -> int:
    resolved_mode = resolve_assistant_mode(mode)

    documents = SimpleDirectoryReader(
        input_files=[path],
    ).load_data()

    return _build_index_from_documents(
        documents=documents,
        mode=resolved_mode,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        append=append,
    )

def build_local_index_snapshot_from_directory(
    *,
    source_directory: str | Path,
    persist_directory: str | Path,
    chunk_size: int = 1200,
    chunk_overlap: int = 150,
) -> int:
    if VECTOR_STORE != "local":
        raise RuntimeError(
            "Local index snapshots can only be built "
            "when VECTOR_STORE is 'local'."
        )

    source_path = Path(source_directory)
    target_path = Path(persist_directory)

    if not source_path.is_dir():
        raise ValueError(
            f"Source directory does not exist: '{source_path}'."
        )

    if target_path.exists() and any(target_path.iterdir()):
        raise ValueError(
            f"Persist directory must be empty: '{target_path}'."
        )

    documents = SimpleDirectoryReader(
        str(source_path),
    ).load_data()

    nodes = _documents_to_nodes(
        documents=documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    index = VectorStoreIndex(
        nodes,
        embed_model=_create_embedding_model(),
    )

    target_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    index.storage_context.persist(
        persist_dir=str(target_path),
    )

    return len(documents)

def get_index(
    mode: AssistantModeInput = None,
) -> VectorStoreIndex | None:
    resolved_mode = resolve_assistant_mode(mode)

    with _local_index_lock:
        return _get_cached_or_persisted_local_index(
            resolved_mode
        )


def reset_local_index(
    mode: AssistantMode | str | None = None,
    *,
    delete_persisted: bool = False,
) -> None:
    with _local_index_lock:
        if mode is None:
            _local_indexes.clear()

            if delete_persisted:
                shutil.rmtree(
                    LOCAL_INDEX_ROOT,
                    ignore_errors=True,
                )

            return

        resolved_mode = AssistantMode(mode)

        _local_indexes.pop(
            resolved_mode,
            None,
        )

        if delete_persisted:
            shutil.rmtree(
                _get_local_index_directory(resolved_mode),
                ignore_errors=True,
            )