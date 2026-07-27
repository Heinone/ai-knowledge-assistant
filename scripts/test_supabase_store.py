from app.vector_store.supabase_store import SupabaseVectorStore

store = SupabaseVectorStore()

chunk_id = store.insert_chunk(
    content="NordicTrail warranty covers broken zippers if the zipper failed because of a manufacturing defect.",
    metadata={
        "source": "test_supabase_store.py",
        "topic": "warranty",
    },
)

print("Inserted chunk id:", chunk_id)

matches = store.search_similar(
    question="Are broken zippers covered by warranty?",
    match_count=3,
)

print("\nMatches:")
for match in matches:
    print("\n---")
    print("ID:", match["id"])
    print("Similarity:", match["similarity"])
    print("Metadata:", match["metadata"])
    print("Content:", match["content"])