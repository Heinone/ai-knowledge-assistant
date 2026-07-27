import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"


class SupabaseVectorStore:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not supabase_url:
            raise RuntimeError("SUPABASE_URL is missing")

        if not supabase_key:
            raise RuntimeError("SUPABASE_SERVICE_KEY is missing")

        if not openai_key:
            raise RuntimeError("OPENAI_API_KEY is missing")

        self.supabase = create_client(supabase_url, supabase_key)
        self.openai = OpenAI(api_key=openai_key)

    def _embed(self, text: str) -> list[float]:
        response = self.openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )

        return response.data[0].embedding

    def insert_chunk(self, content: str, metadata: dict[str, Any]) -> int:
        embedding = self._embed(content)

        result = self.supabase.table("documents").insert(
            {
                "content": content,
                "metadata": metadata,
                "embedding": embedding,
            }
        ).execute()

        return result.data[0]["id"]

    def search_similar(self, question: str, match_count: int = 3) -> list[dict]:
        query_embedding = self._embed(question)

        result = self.supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": match_count,
            },
        ).execute()

        return result.data