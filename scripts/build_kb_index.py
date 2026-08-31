"""
Build a persistent Chroma vector index over the evidence knowledge base.

Run once (or whenever data/evidence_kb.json changes) to (re)build the index.
The index is stored on disk at chroma_db/, so it does not need to be rebuilt
every time the app runs.
"""

import json

import chromadb
from chromadb.utils import embedding_functions

KB_PATH = "data/evidence_kb.json"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "evidence_kb"
EMBED_MODEL = "all-MiniLM-L6-v2"  # small, fast, well-established sentence-transformers model


def main():
    with open(KB_PATH) as f:
        entries = json.load(f)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # if the collection already exists from a previous run, drop it so we
    # always rebuild cleanly from the current knowledge base file
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )

    ids = [e["id"] for e in entries]
    documents = [f"{e['title']}. {e['text']}" for e in entries]
    metadatas = [
        {"reason_code": e["reason_code"], "evidence_type": e["evidence_type"], "title": e["title"]}
        for e in entries
    ]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"Indexed {len(entries)} evidence entries into Chroma collection '{COLLECTION_NAME}'")
    print(f"Persisted at ./{CHROMA_DIR}")

    reason_codes = sorted(set(e["reason_code"] for e in entries))
    print(f"\nReason codes covered ({len(reason_codes)}):")
    for rc in reason_codes:
        count = sum(1 for e in entries if e["reason_code"] == rc)
        print(f"  - {rc}: {count} evidence entries")


if __name__ == "__main__":
    main()