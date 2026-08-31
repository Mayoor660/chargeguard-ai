"""
Evidence letter composer (importable version).

Same logic as scripts/evidence_composer.py, packaged here so it can be
imported directly by the webhook handler instead of only run standalone.
"""

import chromadb
from chromadb.utils import embedding_functions
from jinja2 import Template
import ollama

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "evidence_kb"
EMBED_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"

PROMPT_TEMPLATE = Template("""
You are an assistant helping a merchant respond to a payment dispute (chargeback).
Draft a formal, factual representment letter using ONLY the evidence points listed
below. Do not invent evidence that was not provided. Be concise and professional.

DISPUTE DETAILS
- Reason code: {{ reason_code }}
- Amount: {{ amount }}
- Payment method: {{ payment_method }}

RELEVANT EVIDENCE TYPES TO REFERENCE (use the ones that plausibly apply; do not
claim evidence exists that isn't listed here):
{% for item in evidence_items %}
- {{ item.title }}: {{ item.text }}
{% endfor %}

Write the letter now. Structure it as:
1. Opening statement disputing the chargeback claim
2. A short paragraph per relevant evidence point
3. A closing statement requesting the dispute be reversed

Keep the total length under 300 words.
""".strip())

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        _collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)
    return _collection


def retrieve_evidence(reason_code: str, n_results: int = 4):
    collection = get_collection()
    query_text = reason_code.replace("_", " ")
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"reason_code": reason_code},
    )
    items = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        items.append({"title": meta["title"], "text": doc, "evidence_type": meta["evidence_type"]})
    return items


def validate_letter(letter: str, evidence_items: list) -> dict:
    word_count = len(letter.split())
    issues = []
    if word_count > 400:
        issues.append(f"Letter is long ({word_count} words); expected under ~300.")
    if word_count < 50:
        issues.append(f"Letter is suspiciously short ({word_count} words).")
    if not evidence_items:
        issues.append("No evidence items were retrieved for this reason code.")
    return {"word_count": word_count, "issues": issues, "passed": len(issues) == 0}


def compose_letter(reason_code: str, amount: float, payment_method: str) -> dict:
    evidence_items = retrieve_evidence(reason_code)

    prompt = PROMPT_TEMPLATE.render(
        reason_code=reason_code,
        amount=amount,
        payment_method=payment_method,
        evidence_items=evidence_items,
    )

    response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)
    letter = response["response"].strip()

    validation = validate_letter(letter, evidence_items)

    return {"letter": letter, "evidence_used": evidence_items, "validation": validation}