from dotenv import load_dotenv

load_dotenv()

from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("data/raw/test_fixtures/nordictrail").load_data()

print(f"Loaded documents: {len(documents)}")

for i, doc in enumerate(documents, start=1):
    print("\n" + "=" * 80)
    print(f"DOCUMENT {i}")
    print("Metadata:", doc.metadata)
    print("Text preview:")
    print(doc.text[:500])