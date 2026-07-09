"""
Sovereignty Score — a single 0-100 metric summarizing how well a given
pipeline run upheld Enclave's core guarantees: data residency, audit
verifiability, citation grounding, and single-node execution.
"""
import re


def compute_sovereignty_score(
    data_residency_bytes: int,
    audit_chain_verified: bool,
    single_node_fit: bool,
    auditor_output: str,
) -> dict:
    """
    Scoring breakdown (100 points total):
    - Data residency (40 pts): 40 if 0 bytes left the node, 0 otherwise
    - Audit chain verified (25 pts): 25 if SHA-256 chain is intact
    - Single-node execution (20 pts): 20 if no second GPU was required
    - Citation coverage (15 pts): scaled by % of compliance claims that
      cite a specific Policy ID + Section
    """
    residency_score = 40 if data_residency_bytes == 0 else 0
    chain_score = 25 if audit_chain_verified else 0
    node_score = 20 if single_node_fit else 0

    # Citation coverage: count bullet/claim-like lines vs. lines containing a Policy ID
    claim_lines = [l for l in auditor_output.split("\n") if l.strip().startswith(("-", "*", "1.", "2.", "3.", "4."))]
    cited_lines = [l for l in claim_lines if re.search(r"IP-[\w-]+\s*Section", l)]
    citation_ratio = (len(cited_lines) / len(claim_lines)) if claim_lines else 0
    citation_score = round(citation_ratio * 15, 1)

    total = round(residency_score + chain_score + node_score + citation_score, 1)

    return {
        "sovereignty_score": total,
        "max_score": 100,
        "breakdown": {
            "data_residency": {"score": residency_score, "max": 40, "detail": f"{data_residency_bytes} bytes egress"},
            "audit_chain_verified": {"score": chain_score, "max": 25, "detail": audit_chain_verified},
            "single_node_execution": {"score": node_score, "max": 20, "detail": single_node_fit},
            "citation_coverage": {"score": citation_score, "max": 15, "detail": f"{round(citation_ratio*100)}% of claims cited"},
        },
    }
