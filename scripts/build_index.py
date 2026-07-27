from dotenv import load_dotenv
load_dotenv()

import os

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

api_key = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY loaded:", api_key is not None)

documents = SimpleDirectoryReader("data/raw/test_fixtures/nordictrail").load_data()
print(f"Loaded documents: {len(documents)}")

index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=api_key,
    ),
)

query_engine = index.as_query_engine(
    llm=OpenAI(
        model="gpt-5-mini",
        api_key=api_key,
    ),
)

questions = [

    "What is the refund policy?",

    "How long does shipping to Indonesia take?",

    "Can I return hiking boots after using them once?",

    "Who is the CEO of NordicTrail Gear?",

    "Do you sell motorcycles?",

]

for question in questions:

    print("\n" + "=" * 80)

    print("QUESTION:", question)

    response = query_engine.query(question)

    print("\nANSWER:")

    print(response)

    print("\nSOURCES:")

    for i, node in enumerate(response.source_nodes, start=1):

        print(f"\n--- Source node {i} ---")

        print("Score:", node.score)

        print("Metadata:", node.metadata)

        print("Text preview:", node.text[:300].replace("\n", " "))