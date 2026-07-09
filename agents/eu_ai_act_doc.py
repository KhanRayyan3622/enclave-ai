"""
EU AI Act Annex IV Technical Documentation Generator.

Generates a condensed technical documentation snippet in the structure
required by Annex IV of the EU AI Act for high-risk AI systems, auto-
populated from an actual Enclave pipeline run. This is NOT a substitute
for full legal Annex IV documentation (which requires additional
organizational context Enclave doesn't have), but demonstrates the
data Enclave captures maps directly onto what Annex IV requires.
"""
from datetime import datetime, timezone


def generate_annex_iv_snippet(
    task: str,
    verdict: str,
    framework_coverage: dict,
    sovereignty_score: dict,
    audit_chain_verified: bool,
    model_name: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    eu_sections = framework_coverage.get("eu_ai_act_annex_iv_sections_covered", [])
    frameworks = framework_coverage.get("frameworks_touched", [])

    doc = f"""# EU AI Act — Annex IV Technical Documentation (Auto-Generated Snippet)
Generated: {now}
System: Enclave — Sovereign Multi-Agent Compliance AI

---

## 1. General Description of the AI System
Enclave is a multi-agent AI system (Orchestrator, Researcher, Analyst, Auditor)
that performs automated compliance review of regulated documents (e.g. loan
applications, patient intake forms). It runs entirely on a single AMD Instinct
GPU node, with zero external network egress during inference.

Model in use for this run: {model_name}

## 2. Risk Management System (Annex IV Section 2)
- Every compliance decision requires explicit citation to a specific internal
  Policy ID and Section — claims without a policy citation are not permitted.
- A human escalation packet is automatically generated for any FLAGGED/FAIL
  verdict, routing to the appropriate reviewer role (Underwriter, Compliance
  Officer, Privacy Officer, or DPO) before any adverse action is taken.
- Frameworks engaged by this decision: {', '.join(frameworks) if frameworks else 'None cited in this run'}

## 3. Data Governance (Annex IV Section 3)
- All source data for this decision (task input, policy corpus) originated
  and remained on this node. Data residency: 0 bytes transmitted externally.
- Policy corpus consulted is version-controlled and hash-verified as part of
  the Node Integrity Manifest for this run.

## 4. Accuracy, Robustness (Annex IV Section 4)
- Decision verdict: {verdict}
- Independent second-opinion consistency check performed (Gemma verifier).
- Audit chain integrity (tamper-evidence): {'VERIFIED' if audit_chain_verified else 'NOT VERIFIED'}

## 8. Human Oversight (Annex IV Section 8)
- Verdicts other than PASS automatically generate a human escalation packet
  with specific review items and an SLA (2 business days for FLAGGED,
  1 business day for FAIL).

## Sovereignty & Governance Score
Overall score: {sovereignty_score.get('sovereignty_score', 'N/A')}/100
(See attached breakdown for data residency, audit verification, single-node
execution, and citation-coverage components.)

## EU AI Act Annex IV sections directly evidenced by this run:
{chr(10).join('- ' + s for s in eu_sections) if eu_sections else '- None matched for this specific run'}

---
*This is an auto-generated technical documentation snippet demonstrating
Enclave's evidence capture aligns with Annex IV structure. Full legal
compliance documentation requires additional organizational context
(intended purpose statement, conformity assessment records, post-market
monitoring plan) beyond what a single pipeline run can generate.*
"""
    return doc
