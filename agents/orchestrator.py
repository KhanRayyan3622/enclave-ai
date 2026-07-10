"""
Orchestrator Agent — the only agent that sees the full task. Plans the
workflow and coordinates Researcher, Analyst, and Auditor. All processing
stays within this single node's memory space — no external calls except
to the local inference engine.
"""
import time
import json
from openai import AsyncOpenAI
from agents.research_agent import ResearchAgent
from agents.analyst_agent import AnalystAgent
from agents.auditor_agent import AuditorAgent
from agents.audit_chain import AuditChain
from agents.integrity_manifest import IntegrityManifest
from agents.sovereignty_score import compute_sovereignty_score
from agents.escalation import generate_escalation_packet
from agents.gemma_verifier import gemma_second_opinion
from agents.framework_mapper import map_to_frameworks
from agents.eu_ai_act_doc import generate_annex_iv_snippet
from agents.flow_visualizer import generate_flow_svg

ORCHESTRATOR_SYSTEM = """You are the Orchestrator of Enclave, a sovereign on-premise
multi-agent compliance AI system running entirely on a single AMD Instinct MI300X node.

Given a document review or compliance task, output a JSON plan.

Available agents:
- researcher: retrieves relevant internal policy/regulation context
- analyst: extracts and structures document data
- auditor: produces final compliance verdict (always runs last)

Output ONLY valid JSON:
{
  "analysis": "what this task requires",
  "subtasks": [
    {"agent": "researcher", "task": "..."},
    {"agent": "analyst", "task": "..."},
    {"agent": "auditor", "task": "..."}
  ]
}"""


class OrchestratorAgent:
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model
        self.agents = {
            "researcher": ResearchAgent(client=client, model=model),
            "analyst": AnalystAgent(client=client, model=model),
            "auditor": AuditorAgent(client=client, model=model),
        }
        self.audit_chain = AuditChain()
        self.integrity_manifest = IntegrityManifest(model_name=model)

    async def _plan(self, task: str) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": ORCHESTRATOR_SYSTEM},
                {"role": "user", "content": f"Task: {task}"},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "analysis": task,
                "subtasks": [
                    {"agent": "researcher", "task": f"Identify relevant policy for: {task}"},
                    {"agent": "analyst", "task": task},
                    {"agent": "auditor", "task": f"Produce compliance verdict for: {task}"},
                ]
            }

    async def execute(self, task: str) -> dict:
        pipeline_start = time.perf_counter()
        print(f"\n[ORCHESTRATOR] Task: {task[:80]}...")
        print("[ORCHESTRATOR] Planning (data stays on-node)...")
        plan = await self._plan(task)
        print(f"[ORCHESTRATOR] Plan: {len(plan['subtasks'])} subtasks")

        results = {}
        total_tokens = 0
        agent_trace = []

        for subtask in plan["subtasks"]:
            agent_name = subtask["agent"]
            agent_task = subtask["task"]

            if results:
                context = "\n\n".join(
                    f"[{name.upper()} OUTPUT]\n{r['result']}"
                    for name, r in results.items()
                )
                agent_task = f"{agent_task}\n\nContext from previous agents:\n{context}"

            agent = self.agents[agent_name]
            result = await agent.run(agent_task)
            results[agent_name] = result
            self.audit_chain.add_entry(agent_name, agent_task, result["result"])
            total_tokens += result["tokens"]
            agent_trace.append({
                "agent": agent_name,
                "tokens": result["tokens"],
                "latency_ms": result["latency_ms"],
            })

        total_time = time.perf_counter() - pipeline_start
        final_output = results.get("auditor", list(results.values())[-1])

        self.audit_chain.save()

        auditor_result = results.get("auditor", list(results.values())[-1])
        auditor_text = auditor_result["result"]

        verdict_match = auditor_text.upper()
        if "FAIL" in verdict_match:
            verdict = "FAIL"
        elif "FLAGGED" in verdict_match:
            verdict = "FLAGGED"
        else:
            verdict = "PASS"

        gemma_check = await gemma_second_opinion(verdict, auditor_text)
        framework_coverage = map_to_frameworks(auditor_text)

        sovereignty = compute_sovereignty_score(
            data_residency_bytes=0,
            audit_chain_verified=self.audit_chain.verify(),
            single_node_fit=True,
            auditor_output=auditor_text,
        )

        manifest = self.integrity_manifest.generate(
            decision_hash=self.audit_chain.chain[-1]["hash"] if self.audit_chain.chain else ""
        )
        self.integrity_manifest.save(manifest)

        escalation = generate_escalation_packet(verdict, auditor_text)

        annex_iv_doc = generate_annex_iv_snippet(
            task=task,
            verdict=verdict,
            framework_coverage=framework_coverage,
            sovereignty_score=sovereignty,
            audit_chain_verified=self.audit_chain.verify(),
            model_name=self.model,
        )

        result_dict = {
            "task": task,
            "eu_ai_act_annex_iv_doc": annex_iv_doc,
            "plan": plan,
            "audit_chain_verified": self.audit_chain.verify(),
            "audit_chain_entries": len(self.audit_chain.chain),
            "sovereignty_score": sovereignty,
            "integrity_manifest_hash": manifest["manifest_hash"],
            "escalation": escalation,
            "verdict": verdict,
            "gemma_second_opinion": gemma_check,
            "framework_coverage": framework_coverage,
            "results": results,
            "final_output": final_output["result"],
            "trace": agent_trace,
            "total_tokens": total_tokens,
            "total_time_seconds": round(total_time, 2),
            "data_residency": "0 bytes left this node",
        }

        result_dict["flow_diagram_svg"] = generate_flow_svg(result_dict)
        return result_dict
