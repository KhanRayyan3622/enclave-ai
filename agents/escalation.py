"""
Escalation Packet Generator — when the Auditor returns FLAGGED or FAIL,
produce a structured packet routing the decision to the correct human
reviewer role, matching how a real compliance team hands off edge cases.
"""
import re


ESCALATION_ROLES = {
    "dti": "Senior Underwriter",
    "ltv": "Senior Underwriter",
    "credit": "Senior Underwriter",
    "fair": "Compliance Officer",
    "ecoa": "Compliance Officer",
    "demographic": "Compliance Officer",
    "hipaa": "Privacy Officer",
    "consent": "Privacy Officer",
    "gdpr": "Data Protection Officer",
    "employment": "Senior Underwriter",
}


def generate_escalation_packet(verdict: str, auditor_output: str) -> dict | None:
    """Returns None if verdict is PASS (no escalation needed)."""
    if verdict.upper() == "PASS":
        return None

    text_lower = auditor_output.lower()
    matched_roles = set()
    for keyword, role in ESCALATION_ROLES.items():
        if keyword in text_lower:
            matched_roles.add(role)

    if not matched_roles:
        matched_roles = {"Compliance Officer"}  # default fallback

    # Extract numbered/bulleted "what needs review" items
    review_items = re.findall(r"(?:^\d+\.\s|\-\s)(.+)", auditor_output, re.MULTILINE)
    review_items = [item.strip() for item in review_items if len(item.strip()) > 15][:6]

    return {
        "escalation_required": True,
        "verdict": verdict,
        "routed_to": sorted(matched_roles),
        "priority": "High" if verdict.upper() == "FAIL" else "Medium",
        "review_items": review_items,
        "sla_note": "Per internal policy, FLAGGED items require review within 2 business days; FAIL within 1 business day.",
    }
