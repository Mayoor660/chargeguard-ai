"""
Evidence letter composer (importable version).

Same logic as scripts/evidence_composer.py, packaged here so it can be
imported directly by the webhook handler instead of only run standalone.
"""

import re

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
- Dispute filed on: {{ dispute_date }}
- Reference / tracking ID: {{ tracking_ref }}

RELEVANT EVIDENCE TYPES TO REFERENCE (use the ones that plausibly apply; do not
claim evidence exists that isn't listed here):
{% for item in evidence_items %}
- {{ item.title }}: {{ item.text }}
{% endfor %}

IMPORTANT FORMATTING RULES:
- Do NOT use placeholder brackets like [Date], [Insert Tracking Number], [Address], [Time], or [Email/Message attached].
- Use the exact "Dispute filed on" date and "Reference / tracking ID" given above wherever a date or reference number is needed.
- Do not include a letterhead line, and do not write "[Dear ...]" — just start with "Dear Dispute Resolution Team,".
- If a specific detail is not provided above, do not invent one and do not use a bracket — phrase it generally instead, e.g. "our delivery records confirm successful delivery."

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
    distances = results.get("distances", [[None] * len(results["documents"][0])])[0]

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        distances,
    ):
        similarity = round(1 - dist, 4) if dist is not None else None

        items.append({
            "title": meta["title"],
            "text": doc,
            "evidence_type": meta["evidence_type"],
            "similarity": similarity,
        })

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

    return {
        "word_count": word_count,
        "issues": issues,
        "passed": len(issues) == 0,
    }


def sanitize_letter(letter: str, dispute_date: str, tracking_ref: str) -> str:
    """
    Deterministic cleanup pass. Local LLMs (like llama3.2) don't always follow
    formatting instructions reliably, so we backstop the prompt instructions
    with regex-based normalization rather than trusting the raw output.
    """
    letter = re.sub(r"\[\s*Date\s*\]", dispute_date, letter, flags=re.IGNORECASE)
    letter = re.sub(
        r"\[[^\]]*Tracking[^\]]*\]",
        tracking_ref,
        letter,
        flags=re.IGNORECASE,
    )
    letter = re.sub(
        r"\[[^\]]*Dispute Filed On[^\]]*\]",
        f"Dispute filed on: {dispute_date}",
        letter,
        flags=re.IGNORECASE,
    )
    letter = re.sub(
        r"\[[^\]]*Reference[^\]]*\]",
        tracking_ref,
        letter,
        flags=re.IGNORECASE,
    )

    letter = re.sub(
        r"\[\s*Merchant'?s? Letterhead\s*\]\n?",
        "",
        letter,
        flags=re.IGNORECASE,
    )
    letter = re.sub(
        r"\[\s*Dear[^\]]*\]",
        "Dear Dispute Resolution Team,",
        letter,
        flags=re.IGNORECASE,
    )
    letter = re.sub(
        r"\[\s*Merchant'?s? Name\s*\]",
        "Merchant Support Team",
        letter,
        flags=re.IGNORECASE,
    )

    # Catch-all: strip brackets from anything still left, keep the inner text
    letter = re.sub(r"\[([^\]]+)\]", r"\1", letter)

    # Clean up extra blank lines
    letter = re.sub(r"\n{3,}", "\n\n", letter).strip()

    return letter


def compose_letter(
    reason_code: str,
    amount: float,
    payment_method: str,
    dispute_date: str = None,
    tracking_ref: str = None,
) -> dict:
    evidence_items = retrieve_evidence(reason_code)

    dispute_date = dispute_date or "the date on file"
    tracking_ref = tracking_ref or "the reference on file"

    prompt = PROMPT_TEMPLATE.render(
        reason_code=reason_code,
        amount=amount,
        payment_method=payment_method,
        dispute_date=dispute_date,
        tracking_ref=tracking_ref,
        evidence_items=evidence_items,
    )

    response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)
    letter = response["response"].strip()
    letter = sanitize_letter(letter, dispute_date, tracking_ref)

    validation = validate_letter(letter, evidence_items)

    return {
        "letter": letter,
        "evidence_used": evidence_items,
        "validation": validation,
    }