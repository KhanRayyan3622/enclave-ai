"""
Auditor Agent — produces the final compliance verdict, the way a human
compliance officer would sign off on a case.
"""
from agents.base_agent import BaseAgent

AUDITOR_SYSTEM = """You are the Auditor Agent inside Enclave, a sovereign on-premise
compliance AI system running on AMD Instinct MI300X.

Your job: review the research context and analyst findings, then produce
a final compliance verdict.

Always provide:
1. Verdict: PASS / FLAGGED / FAIL
2. Confidence level (High/Medium/Low)
3. Specific reasoning citing what was checked
4. If FLAGGED or FAIL: exactly what needs human review and why"""


class AuditorAgent(BaseAgent):
    def __init__(self, client, model):
        super().__init__(client, model)
        self.name = "auditor"

    async def run(self, task: str) -> dict:
        print(f"  [AUDITOR] Producing compliance verdict: {task[:60]}...")
        return await self._call(system=AUDITOR_SYSTEM, user=task, max_tokens=1500)
