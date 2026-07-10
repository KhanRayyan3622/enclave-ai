"""
Re-Audit / Drift Check — re-runs a previously reviewed task and compares
the new result against the original, flagging any drift in verdict,
sovereignty score, or cited policies. Demonstrates continuous
audit-readiness: proof that a decision remains consistent (or correctly
changes) as policies or model behavior evolve over time.
"""
from dataclasses import dataclass


@dataclass
class DriftResult:
    verdict_changed: bool
    original_verdict: str
    new_verdict: str
    score_delta: float
    original_score: float
    new_score: float
    citation_overlap_pct: float
    original_citations: list[str]
    new_citations: list[str]
    drift_detected: bool
    summary: str


def compare_runs(original_result: dict, new_result: dict) -> DriftResult:
    orig_verdict = original_result.get("verdict", "UNKNOWN")
    new_verdict = new_result.get("verdict", "UNKNOWN")
    verdict_changed = orig_verdict != new_verdict

    orig_score = original_result.get("sovereignty_score", {}).get("sovereignty_score", 0)
    new_score = new_result.get("sovereignty_score", {}).get("sovereignty_score", 0)
    score_delta = round(new_score - orig_score, 1)

    orig_citations = set(original_result.get("framework_coverage", {}).get("cited_policy_ids", []))
    new_citations = set(new_result.get("framework_coverage", {}).get("cited_policy_ids", []))

    if orig_citations or new_citations:
        overlap = len(orig_citations & new_citations)
        union = len(orig_citations | new_citations)
        citation_overlap_pct = round((overlap / union) * 100, 1) if union > 0 else 100.0
    else:
        citation_overlap_pct = 100.0

    drift_detected = verdict_changed or abs(score_delta) > 5 or citation_overlap_pct < 80

    if drift_detected:
        summary = (
            f"DRIFT DETECTED: verdict {'changed from ' + orig_verdict + ' to ' + new_verdict if verdict_changed else 'unchanged (' + orig_verdict + ')'}, "
            f"score delta {score_delta:+.1f}, citation overlap {citation_overlap_pct}%. "
            f"Recommend human review of this case before relying on the re-audit result."
        )
    else:
        summary = (
            f"NO DRIFT: verdict consistent ({orig_verdict}), score delta {score_delta:+.1f} "
            f"(within tolerance), citation overlap {citation_overlap_pct}%. Decision remains stable."
        )

    return DriftResult(
        verdict_changed=verdict_changed,
        original_verdict=orig_verdict,
        new_verdict=new_verdict,
        score_delta=score_delta,
        original_score=orig_score,
        new_score=new_score,
        citation_overlap_pct=citation_overlap_pct,
        original_citations=sorted(orig_citations),
        new_citations=sorted(new_citations),
        drift_detected=drift_detected,
        summary=summary,
    )
