"""
Local Policy Retriever — simple keyword-based retrieval over the local
policy corpus. Deliberately NOT a call to any external vector DB or API:
retrieval happens entirely from files on this node, preserving the
zero-egress guarantee even for "RAG" lookups.
"""
import os
import re
from pathlib import Path

POLICY_DIR = Path(__file__).parent.parent / "policies"


def load_policies() -> dict[str, str]:
    policies = {}
    for f in POLICY_DIR.glob("*.md"):
        policies[f.stem] = f.read_text()
    return policies


def retrieve_relevant_sections(query: str, top_k: int = 3) -> list[dict]:
    """
    Simple keyword-overlap retrieval over policy sections.
    Splits each policy doc into ## Section chunks, scores by keyword overlap.
    """
    policies = load_policies()
    query_terms = set(re.findall(r"\w+", query.lower()))

    chunks = []
    for doc_name, text in policies.items():
        sections = re.split(r"(?=## Section)", text)
        for section in sections:
            if not section.strip() or "Policy ID" in section[:50]:
                continue
            section_terms = set(re.findall(r"\w+", section.lower()))
            overlap = len(query_terms & section_terms)
            if overlap > 0:
                # extract policy ID from doc header if present
                id_match = re.search(r"Policy ID:\s*([\w-]+)", text)
                policy_id = id_match.group(1) if id_match else doc_name
                title_match = re.search(r"## (Section [\d.]+ — .+)", section)
                title = title_match.group(1) if title_match else "General"
                chunks.append({
                    "policy_id": policy_id,
                    "section": title,
                    "text": section.strip(),
                    "score": overlap,
                })

    chunks.sort(key=lambda c: c["score"], reverse=True)
    return chunks[:top_k]


def format_citations(chunks: list[dict]) -> str:
    """Format retrieved chunks as citable context for agent prompts."""
    if not chunks:
        return "No specific internal policy sections matched this query."
    formatted = []
    for c in chunks:
        formatted.append(f"[{c['policy_id']} — {c['section']}]\n{c['text']}")
    return "\n\n".join(formatted)
