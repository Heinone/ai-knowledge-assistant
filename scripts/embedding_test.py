import os
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

texts = [
    "The rapper performed on stage.",
    "The artist entertained the crowd.",
    "A musician played music for the audience."
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embeddings = [item.embedding for item in response.data]

def compare(i, j):
    score = cosine_similarity(
        [embeddings[i]],
        [embeddings[j]]
    )[0][0]

    print(f'"{texts[i]}" vs "{texts[j]}" similarity: {score:.4f}')

compare(0, 1)
compare(0, 2)
compare(1, 2)