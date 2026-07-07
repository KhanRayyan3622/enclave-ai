"""
Research Agent — retrieves relevant internal policy, regulation, or
guideline context. In production, this agent queries only local/internal
document stores (never external APIs), preserving the zero-data-egress
guarantee.
"""
from agents.base_agent import BaseAgent

RESEARCH_SYSTEM = """You are the Research Agent inside Enclave, a sovereign on-premise
compliance AI system running on AMD Instinct MI300X.

Your job: given a document review task, identify what internal policies,
regulations, or guidelines are relevant. Note: in this Enclave deployment,
all context is retrieved from local/internal sources only — nothing is
looked up externally.

Provide:
1. Relevant policy/regulation areas
2. Key requirements or thresholds that apply
3. Common red flags reviewers should watch for"""


class ResearchAgent(BaseAgent):
    def __init__(self, client, model):
        super().__init__(client, model)
        self.name = "researcher"

    async def run(self, task: str) -> dict:
        print(f"  [RESEARCHER] Retrieving policy context: {task[:60]}...")
        return await self._call(system=RESEARCH_SYSTEM, user=task, max_tokens=1500)
