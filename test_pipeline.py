"""
Enclave — Full Pipeline Test
"""
import asyncio
from inference.fireworks_client import get_client, DEFAULT_MODEL
from agents.orchestrator import OrchestratorAgent

async def main():
    print("="*60)
    print("ENCLAVE — Sovereign Multi-Agent Compliance Pipeline")
    print(f"Model: {DEFAULT_MODEL}")
    print("="*60)

    client = get_client()
    orchestrator = OrchestratorAgent(client=client, model=DEFAULT_MODEL)

    task = """Review this loan application summary for lending compliance:
Applicant: John Doe, Annual Income: $65,000, Requested Loan: $450,000,
Debt-to-Income Ratio: 42%, Credit Score: 680, Employment: 8 months at current job.
Check against standard fair-lending and DTI threshold guidelines."""

    result = await orchestrator.execute(task)

    print("\n" + "="*60)
    print("PIPELINE RESULT")
    print("="*60)
    print(f"Data residency: {result['data_residency']}")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Total time: {result['total_time_seconds']}s")
    print(f"\nAgent trace:")
    for step in result['trace']:
        print(f"  {step['agent']:12} | {step['tokens']:4} tokens | {step['latency_ms']:.0f}ms")
    print(f"\n--- FINAL AUDITOR VERDICT ---")
    print(result['final_output'])

asyncio.run(main())
