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

content = "NordicTrail Gear offers shipping to Indonesia. Shipping to Indonesia usually takes 7 to 14 business days."

embedding_response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=content,
)

embedding = embedding_response.data[0].embedding

result = supabase.table("documents").insert(
    {
        "content": content,
        "metadata": {
            "source": "manual_test",
            "topic": "shipping",
        },
        "embedding": embedding,
    }
).execute()

print(result)