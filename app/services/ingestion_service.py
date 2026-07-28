import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from app.config.env_config import VECTOR_STORE
from app.vector_store.supabase_store import SupabaseVectorStore

_index = None
_local_nodes: list[Any] = []


def _get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")
    return api_key


def _documents_to_nodes(
    documents: list[Any],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
):
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    nodes = splitter.get_nodes_from_documents(documents)

    print(
        {
            "documents_loaded": len(documents),
            "chunks_created": len(nodes),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "vector_store": VECTOR_STORE,
        }
    )

    return nodes


def _build_local_index_from_nodes(nodes, append: bool = False) -> None:
    global _index
    global _local_nodes

    api_key = _get_api_key()

    if append:
        _local_nodes.extend(nodes)
    else:
        _local_nodes = list(nodes)

    _index = VectorStoreIndex(
        _local_nodes,
        embed_model=OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=api_key,
        ),
    )

    print(
        {
            "local_index_total_chunks": len(_local_nodes),
            "append": append,
        }
    )


def _insert_nodes_into_supabase(nodes) -> None:
    store = SupabaseVectorStore()

    for i, node in enumerate(nodes, start=1):
        metadata = dict(node.metadata)
        metadata["chunk_number"] = i

        inserted_id = store.insert_chunk(
            content=node.text,
            metadata=metadata,
        )

        print(
            {
                "inserted_id": inserted_id,
                "source": metadata.get("file_name"),
                "chunk_number": i,
            }
        )


def _build_index_from_documents(
    documents,
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
        _insert_nodes_into_supabase(nodes)
    else:
        _build_local_index_from_nodes(
            nodes=nodes,
            append=append,
        )

    return len(documents)


def build_index_from_directory(
    path: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    append: bool = False,
) -> int:
    documents = SimpleDirectoryReader(path).load_data()

    return _build_index_from_documents(
        documents=documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        append=append,
    )


def build_index_from_file(
    path: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    append: bool = False,
) -> int:
    documents = SimpleDirectoryReader(input_files=[path]).load_data()

    return _build_index_from_documents(
        documents=documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        append=append,
    )


def get_index():
    return _index


def reset_local_index() -> None:
    global _index
    global _local_nodes

    _index = None
    _local_nodes = []