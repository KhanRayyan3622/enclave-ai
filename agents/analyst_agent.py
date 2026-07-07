"""
Analyst Agent — extracts and processes document data: fields, figures,
entities, structured content. The "reading" work of the pipeline.
"""
from agents.base_agent import BaseAgent

ANALYST_SYSTEM = """You are the Analyst Agent inside Enclave, a sovereign on-premise
compliance AI system running on AMD Instinct MI300X.

Your job: extract and structure the relevant data from the document or
task provided. Identify key fields, figures, entities, dates, and any
inconsistencies or missing required information.

Provide:
1. Structured extraction of key data points
2. Any missing required fields
3. Any inconsistencies or anomalies noticed"""


class AnalystAgent(BaseAgent):
    def __init__(self, client, model):
        super().__init__(client, model)
        self.name = "analyst"

    async def run(self, task: str) -> dict:
        print(f"  [ANALYST] Processing document: {task[:60]}...")
        return await self._call(system=ANALYST_SYSTEM, user=task, max_tokens=2000)
