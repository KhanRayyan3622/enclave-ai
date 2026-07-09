"""
Research Agent — retrieves relevant internal policy sections via LOCAL
keyword retrieval (agents/policy_retriever.py), never an external call.
Grounds downstream agents in citable, verifiable policy text.
"""
from agents.base_agent import BaseAgent
from agents.policy_retriever import retrieve_relevant_sections, format_citations

RESEARCH_SYSTEM = """You are the Research Agent inside Enclave, a sovereign on-premise
compliance AI system running on AMD Instinct MI300X.

You have been provided with RETRIEVED POLICY SECTIONS below, retrieved from local
internal policy documents (never an external source). Summarize which sections are
relevant to the task and why. ALWAYS cite the exact Policy ID and Section number
when referencing a requirement — e.g. "per IP-ADM-042 Section 3.1"."""


class ResearchAgent(BaseAgent):
    def __init__(self, client, model):
        super().__init__(client, model)
        self.name = "researcher"

    async def run(self, task: str) -> dict:
        print(f"  [RESEARCHER] Retrieving local policy context: {task[:60]}...")
        chunks = retrieve_relevant_sections(task, top_k=3)
        citations = format_citations(chunks)
        enriched_task = f"{task}\n\n--- RETRIEVED POLICY SECTIONS (local corpus) ---\n{citations}"
        result = await self._call(system=RESEARCH_SYSTEM, user=enriched_task, max_tokens=1500)
        result["citations_used"] = [c["policy_id"] + " " + c["section"] for c in chunks]
        return result
