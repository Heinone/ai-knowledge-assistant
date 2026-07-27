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

chunks = [
    {
        "content": "Customers may return unused products within 30 days of purchase for a full refund. Used hiking boots are not eligible for a refund unless defective.",
        "metadata": {"source": "refund_policy.txt", "topic": "refund"},
    },
    {
        "content": "Shipping to Indonesia is available and usually takes 7 to 14 business days. Domestic shipping usually takes 3 to 5 business days.",
        "metadata": {"source": "shipping_policy.txt", "topic": "shipping"},
    },
    {
        "content": "NordicTrail products include a 1-year limited warranty against manufacturing defects. Broken zippers are covered if caused by manufacturing defects.",
        "metadata": {"source": "warranty_policy.txt", "topic": "warranty"},
    },
]

for chunk in chunks:
    embedding_response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk["content"],
    )

    embedding = embedding_response.data[0].embedding

    result = supabase.table("documents").insert(
        {
            "content": chunk["content"],
            "metadata": chunk["metadata"],
            "embedding": embedding,
        }
    ).execute()

    print("Inserted:", chunk["metadata"]["source"], result.data[0]["id"])