"""
Batch Processor — runs multiple compliance reviews from a CSV of cases
and produces a summary (pass/flagged/fail counts) plus per-row detail.
Demonstrates enterprise-scale usage: a bank processing its daily
pipeline of applications, not just one ad-hoc review.
"""
import csv
import io
import asyncio
from dataclasses import dataclass


@dataclass
class BatchRow:
    row_id: int
    task: str
    verdict: str
    sovereignty_score: float
    escalation_required: bool


async def process_batch_csv(csv_content: str, orchestrator, max_concurrent: int = 2) -> dict:
    """
    csv_content: raw CSV text with columns [id, task_description]
    orchestrator: an initialized OrchestratorAgent instance
    max_concurrent: limit concurrent pipeline runs (avoid overwhelming the backend)
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)

    if not rows:
        return {"error": "CSV is empty or malformed. Expected columns: id, task_description"}

    semaphore = asyncio.Semaphore(max_concurrent)
    results: list[BatchRow] = []

    async def process_row(row: dict):
        async with semaphore:
            row_id = int(row.get("id", 0))
            task = row.get("task_description", "")
            if not task.strip():
                return BatchRow(row_id, task, "SKIPPED", 0, False)

            pipeline_result = await orchestrator.execute(task)
            return BatchRow(
                row_id=row_id,
                task=task[:80],
                verdict=pipeline_result["verdict"],
                sovereignty_score=pipeline_result["sovereignty_score"]["sovereignty_score"],
                escalation_required=pipeline_result["escalation"] is not None,
            )

    tasks = [process_row(row) for row in rows]
    results = await asyncio.gather(*tasks)

    pass_count = sum(1 for r in results if r.verdict == "PASS")
    flagged_count = sum(1 for r in results if r.verdict == "FLAGGED")
    fail_count = sum(1 for r in results if r.verdict == "FAIL")
    avg_score = round(sum(r.sovereignty_score for r in results) / len(results), 1) if results else 0

    return {
        "total_processed": len(results),
        "summary": {
            "pass": pass_count,
            "flagged": flagged_count,
            "fail": fail_count,
        },
        "avg_sovereignty_score": avg_score,
        "escalations_required": sum(1 for r in results if r.escalation_required),
        "rows": [
            {
                "id": r.row_id,
                "task": r.task,
                "verdict": r.verdict,
                "sovereignty_score": r.sovereignty_score,
                "escalation_required": r.escalation_required,
            }
            for r in results
        ],
    }
