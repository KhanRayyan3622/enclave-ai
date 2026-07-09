"""
Multi-Framework Compliance Mapper — tags internal policy citations with
the broader regulatory frameworks they satisfy: EU AI Act (Annex IV),
NIST AI RMF (Govern/Map/Measure/Manage), ISO/IEC 42001, and the
underlying sector law (GDPR, HIPAA, ECOA/Reg B).

This does not change what the Auditor decides — it adds a second layer
of labeling so a compliance officer (or regulator) can immediately see
which cross-cutting framework each internal policy citation satisfies.
"""
import re

FRAMEWORK_MAP = {
    "IP-ADM-042": {
        "frameworks": ["NIST AI RMF (Measure)", "ISO/IEC 42001 (Clause 8.2)"],
        "sector_law": "ECOA / Regulation B (Fair Lending)",
        "eu_ai_act_annex_iv": "Section 2 (Risk Management System) & Section 4 (Accuracy/Robustness)",
    },
    "IP-PRIV-039": {
        "frameworks": ["NIST AI RMF (Govern)", "ISO/IEC 42001 (Clause 8.3)"],
        "sector_law": "HIPAA Privacy Rule (45 CFR §164.508)",
        "eu_ai_act_annex_iv": "Section 3 (Data Governance)",
    },
    "IP-LEGAL-011": {
        "frameworks": ["NIST AI RMF (Govern)", "ISO/IEC 42001 (Clause 8.3)"],
        "sector_law": "GDPR Articles 5, 6, 28",
        "eu_ai_act_annex_iv": "Section 3 (Data Governance) & Section 8 (Human Oversight)",
    },
}


def extract_policy_ids(text: str) -> list[str]:
    normalized = text.replace("\u2011", "-").replace("\u2010", "-").replace("\u2013", "-")
    return sorted(set(re.findall(r"IP-[A-Z]+-\d+", normalized)))


def map_to_frameworks(auditor_text: str) -> dict:
    cited_ids = extract_policy_ids(auditor_text)
    coverage = {}
    for policy_id in cited_ids:
        if policy_id in FRAMEWORK_MAP:
            coverage[policy_id] = FRAMEWORK_MAP[policy_id]

    all_frameworks = set()
    all_eu_sections = set()
    for entry in coverage.values():
        all_frameworks.update(entry["frameworks"])
        all_eu_sections.add(entry["eu_ai_act_annex_iv"])

    return {
        "cited_policy_ids": cited_ids,
        "policy_framework_coverage": coverage,
        "frameworks_touched": sorted(all_frameworks),
        "eu_ai_act_annex_iv_sections_covered": sorted(all_eu_sections),
    }
