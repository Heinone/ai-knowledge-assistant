from dotenv import load_dotenv

load_dotenv()

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

documents = SimpleDirectoryReader("data/raw/test_fixtures/nordictrail").load_data()

chunk_sizes = [128, 256, 512, 1024]

for chunk_size in chunk_sizes:
    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=40,
    )

    nodes = splitter.get_nodes_from_documents(documents)

    print("\n" + "#" * 100)
    print(f"CHUNK SIZE: {chunk_size}")
    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(nodes)}")

    for i, node in enumerate(nodes, start=1):
        print("\n" + "=" * 80)
        print(f"CHUNK {i}")
        print("Source:", node.metadata.get("file_name"))
        print("Text preview:")
        print(node.text[:500])