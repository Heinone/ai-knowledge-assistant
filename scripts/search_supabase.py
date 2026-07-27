from dotenv import load_dotenv

load_dotenv()

import os
from openai import OpenAI
from supabase import create_client

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY"),
)

question = "Are broken zippers covered by warranty?"

embedding_response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=question,
)

query_embedding = embedding_response.data[0].embedding

result = supabase.rpc(
    "match_documents",
    {
        "query_embedding": query_embedding,
        "match_count": 3,
    },
).execute()

print("Matches:")
for row in result.data:
    print("\n---")
    print("ID:", row["id"])
    print("Similarity:", row["similarity"])
    print("Metadata:", row["metadata"])
    print("Content:", row["content"])