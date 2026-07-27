from dotenv import load_dotenv

load_dotenv()

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

text = "NordicTrail Gear offers 7 to 14 business day shipping to Indonesia."

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text,
)

embedding = response.data[0].embedding

print("Embedding length:", len(embedding))
print("First 5 values:", embedding[:5])