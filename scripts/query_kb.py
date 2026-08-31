"""
Quick sanity check: given a reason_code, retrieve the most relevant evidence
guidance from the Chroma index.

This is just a manual test harness -- the real pipeline will call the same
retrieval pattern from the evidence composer in a later step.
"""

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "evidence_kb"
EMBED_MODEL = "all-MiniLM-L6-v2"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)


def query_by_reason_code(collection, reason_code: str, n_results: int = 5):
    # semantic query text derived from the reason code, since Chroma searches
    # by meaning, not exact metadata match alone
    query_text = reason_code.replace("_", " ")
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"reason_code": reason_code},
    )
    return results


if __name__ == "__main__":
    collection = get_collection()

    test_reason_codes = ["product_not_received", "fraudulent", "subscription_canceled"]

    for rc in test_reason_codes:
        print(f"\n{'=' * 60}")
        print(f"Reason code: {rc}")
        print("=" * 60)
        results = query_by_reason_code(collection, rc)
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            print(f"\n  [{meta['evidence_type']}] (distance: {dist:.4f})")
            print(f"  {doc}")