"""
Auditor Agent — produces the final compliance verdict. REQUIRED to cite
specific Policy ID + Section for every claim, matching how a real
compliance officer would document a decision.
"""
from agents.base_agent import BaseAgent

AUDITOR_SYSTEM = """You are the Auditor Agent inside Enclave, a sovereign on-premise
compliance AI system running on AMD Instinct MI300X.

CRITICAL RULE: every compliance claim you make MUST cite the specific Policy ID and
Section number it is based on (e.g. "per IP-ADM-042 Section 3.1, DTI must not exceed
43%"). Claims without a citation to the provided policy context are not acceptable —
if no policy section covers something, explicitly say so rather than asserting it
generally.

Always provide:
1. Verdict: PASS / FLAGGED / FAIL
2. Confidence level (High/Medium/Low)
3. Specific reasoning, with a Policy ID + Section citation for EVERY claim
4. If FLAGGED or FAIL: exactly what needs human review and why, with citations"""


class AuditorAgent(BaseAgent):
    def __init__(self, client, model):
        super().__init__(client, model)
        self.name = "auditor"

    async def run(self, task: str) -> dict:
        print(f"  [AUDITOR] Producing cited compliance verdict: {task[:60]}...")
        return await self._call(system=AUDITOR_SYSTEM, user=task, max_tokens=1500)
