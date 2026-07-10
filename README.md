# 🔒 Enclave

> **The multi-agent AI system that never leaves the building.**
> A sovereign, on-premise agentic AI compliance platform that runs entirely inside a single AMD Instinct GPU node — built for banks, hospitals, and government agencies that legally cannot send sensitive data to cloud APIs.

[![AMD MI300X](https://img.shields.io/badge/AMD-MI300X-ED1C24?style=flat)](https://www.amd.com/en/products/accelerators/instinct/mi300.html)
[![ROCm](https://img.shields.io/badge/ROCm-7.2-blue)](https://rocm.docs.amd.com/)
[![vLLM](https://img.shields.io/badge/vLLM-0.16-green)](https://github.com/vllm-project/vllm)
[![Docker](https://img.shields.io/badge/Docker-Verified%20Build-2496ED?logo=docker)](Dockerfile)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Landing page:** [`landing/index.html`](landing/index.html) · **Dashboard:** `python -m dashboard.app` · **API:** `python api.py`

---

## ✅ Verified, not claimed

Every number in this README was measured on real infrastructure — either AMD Instinct hardware via AMD Developer Cloud, or the project's own Docker/API stack, running end to end. Where something is a hackathon-scale simplification rather than a production claim, we say so explicitly.

---

## The problem

Regulated organizations — banks doing loan underwriting, hospitals processing intake forms, government agencies reviewing filings — want the productivity of agentic AI. But sending patient records, financial filings, or classified documents to OpenAI, Anthropic, or any cloud API is often a compliance violation before the first token is even generated. Data residency laws (GDPR, HIPAA, PCI-DSS, and sovereign-AI mandates across the EU, Gulf, and Asia) require sensitive data to never leave a controlled environment. The EU AI Act's high-risk obligations become broadly applicable **August 2, 2026** — weeks from this hackathon — making this an urgent, not theoretical, problem.

Most "on-prem AI" solutions solve this by running one small model on one small GPU — a fraction of what cloud-based agentic AI can do. Enclave removes that tradeoff.

## The solution

Enclave runs a complete multi-agent pipeline — **Orchestrator → Researcher → Analyst → Auditor** — entirely inside **one** AMD Instinct GPU. No data crosses a network boundary. No API call ever leaves the building.

This is only possible because of one specific hardware fact: production AMD Instinct MI300X nodes offer up to **192GB of HBM3 memory on a single GPU** (our hackathon demo runs on a 48GB shared allocation — see [Hardware Notes](#hardware-notes)). Fitting a multi-agent pipeline — multiple agent contexts, a shared KV-cache pool, and a production-size model — into one GPU is the difference between:

- **On MI300X:** one box, one power cord, zero network exposure, fully auditable
- **On H100 (80GB):** 2–3 GPUs networked together to fit the same workload — every network hop between GPUs is an additional attack surface a compliance auditor has to sign off on

Enclave turns AMD's memory advantage into a literal compliance advantage — and doesn't stop there. Every decision is policy-cited, cryptographically auditable, and independently verifiable.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    ENCLAVE — Single AMD Instinct Node               │
│                    (Air-gapped / VPC-isolated boundary)            │
│                                                                    │
│   Document/Task In ──▶ ┌─────────────────────┐                    │
│                        │  Orchestrator Agent │                    │
│                        └──────────┬───────────┘                   │
│              ┌────────────────────┼────────────────────┐          │
│              ▼                    ▼                    ▼          │
│     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│     │ Research Agent  │  │ Analyst Agent  │  │ Auditor Agent  │   │
│     │ local policy    │  │ data extraction│  │ cited verdict  │   │
│     │ retrieval       │  │                │  │ PASS/FLAG/FAIL │   │
│     └────────┬────────┘  └───────┬────────┘  └───────┬────────┘   │
│              └────────────────────┼────────────────────┘          │
│                                   ▼                                │
│     Shared Inference Engine — vLLM + ROCm — Shared KV-Cache        │
│                                   ▼                                │
│   ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│   │ SHA-256 Audit│ Framework Map│ Sovereignty  │ Gemma Second │  │
│   │ Chain        │ (EU AI Act,  │ Score        │ Opinion      │  │
│   │              │ NIST, ISO)   │              │              │  │
│   └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                                                                    │
│         🔒 Result Out ── 0 bytes left this node ── 🔒              │
└──────────────────────────────────────────────────────────────────┘
```

| Agent | Role |
|-------|------|
| **Orchestrator** | Plans the workflow — the only agent that sees the full task |
| **Researcher** | Retrieves relevant policy from a **local** corpus via keyword retrieval — never an external call |
| **Analyst** | Extracts and structures the document data — fields, figures, entities |
| **Auditor** | Issues the final verdict (PASS / FLAGGED / FAIL) — **every claim must cite a specific internal Policy ID and Section**, or it isn't accepted |

---

## Real hardware results

Captured live on AMD Developer Cloud (ROCm 7.2, vLLM 0.16.1, PyTorch 2.9), on a 48GB shared MI300X allocation:

| Metric | Value |
|---|---|
| Model | Qwen/Qwen2-7B-Instruct |
| Model weights loaded | 14.35 GiB (well under the 48GB allocation — real headroom to spare) |
| Model load time | 9.3s |
| KV cache allocated | 3.03 GiB → 56,768 tokens capacity |
| Single-agent pipeline (Research→Audit) | 776 tokens in 23.64s → **32.8 tok/s** |

### Concurrent multi-agent proof — measured, not architectural claim only

A natural question: does Enclave actually run agents *concurrently* with real shared-context reuse, or is that just a diagram? We measured it directly, batching all 4 agents into a single `vLLM.chat()` call sharing a system-level prefix:

| Run | Tokens | Time | Throughput |
|---|---|---|---|
| 4 agents, concurrent, shared prefix | 1,149 | 18.02s | **63.8 tok/s** |
| 1 agent, cold, unrelated prompt (baseline) | 300 | 9.09s | 33.0 tok/s |

**→ 1.9× throughput from running all 4 agents together on a single node.**

*Methodology note, in the interest of honesty: our first attempt used raw prompt concatenation instead of proper chat templating, which caused the small instruction-tuned model to occasionally drift off-task under batched generation. Switching to vLLM's `chat()` method with correct message-role formatting fixed this completely — the numbers above are from the corrected, validated run. Full data: [`results/concurrent_4agent_proof.json`](results/concurrent_4agent_proof.json).*

---

## What makes this a product, not a demo

### 1. Grounded policy citations
The Auditor cannot make a compliance claim without citing a specific Policy ID and Section from a local policy corpus (`policies/`). No citation, no claim.

### 2. Tamper-evident SHA-256 audit chain
Every agent step is chained: `hash(prev_hash + agent + task + output + timestamp)`. Independently re-verifiable — we tested this by deliberately corrupting one character in a saved chain and confirmed the system correctly detects the break:
```json
{"verified": false, "entries_checked": 1, "detail": "Chain broken at entry 1: prev_hash mismatch (possible tampering)"}
```

### 3. Public verification endpoint (`POST /verify`)
Anyone — a judge, an auditor, a regulator — can paste an audit chain JSON and independently recompute the hash chain without needing access to Enclave's internal state.

### 4. Multi-framework compliance mapping
Every policy citation is tagged with the broader regulatory frameworks it satisfies: **EU AI Act Annex IV**, **NIST AI RMF** (Govern/Map/Measure/Manage), **ISO/IEC 42001**, plus the underlying sector law (ECOA, HIPAA, GDPR).

### 5. EU AI Act Annex IV documentation generator
Auto-generates a technical documentation snippet in Annex IV structure (Risk Management, Data Governance, Accuracy/Robustness, Human Oversight) populated from the actual run — directly relevant to the EU's August 2026 deadline.

### 6. Regulator-Ready Evidence Package (PDF)
One call bundles the verdict, citations, escalation packet, sovereignty score, framework coverage, Gemma second opinion, and Annex IV appendix into a single professional PDF — the artifact a compliance officer would actually file. Generated and rendered successfully in testing (3 pages, color-coded verdict, formatted tables).

### 7. Sovereignty Score (0–100)
A single memorable metric: data residency (40pts) + audit chain verified (25pts) + single-node execution (20pts) + citation coverage (15pts). Real runs scored 85–94/100.

### 8. Human escalation packets
Any FLAGGED/FAIL verdict auto-generates a structured packet routing to the correct role (Senior Underwriter, Compliance Officer, Privacy Officer, DPO) with a specific SLA — no silent auto-denials.

### 9. Real Gemma second-opinion verification
An independent consistency check using Google's Gemma model (`gemma-4-26b-a4b-it`), confirmed working with a real API call — genuinely checks whether the Auditor's verdict is internally consistent with its own reasoning.

### 10. Re-audit / drift detection
Re-runs a case and diffs the new result against the original — flagging verdict changes, sovereignty score drift beyond tolerance, or citation-set changes. Tested live: caught an 8.3-point score drift between two runs of the same case even though the verdict stayed consistent — proof the check has real teeth, not just a rubber stamp.

### 11. REST API (FastAPI)
`/health`, `/review`, `/review/pdf`, `/review/diagram`, `/verify`, `/reaudit` — a real, callable service any loan-origination or EHR system could integrate, not just a UI. All endpoints tested end-to-end with real requests and real responses.

### 12. Batch CSV processing
Upload a CSV of cases, get a pass/flagged/fail summary plus per-row detail, processed concurrently. Tested with 3 real applications — correctly and consistently held every case to the same completeness standard, regardless of how strong the applicant's financials looked, exactly as internal policy requires.

### 13. Decision flow visualization
Auto-generated SVG diagram of the actual run — agents, real token counts, real latencies, verdict-colored Auditor box, escalation routing — for dashboards and demo material.

### 14. Auto-tuner with single-node hard constraint
Sweeps batch size, KV-cache dtype, and speculative decoding — but any configuration requiring a second GPU is automatically rejected, regardless of raw speed, because a network hop between GPUs breaks the zero-egress guarantee.

---

## Why this can't just be a cloud API

| | Cloud API | Enclave on AMD Instinct |
|---|---|---|
| Data leaves the building | Yes, every request | Never |
| Network hops for multi-agent workload | N/A (data already left) | 0 — single node |
| GPUs needed at production scale | 2–3× H100 (80GB each) | 1× MI300X (192GB) |
| Every claim cited to policy | Rarely enforced | Required |
| Tamper-evidence | Vendor's word | SHA-256 chain, independently verifiable |
| Auditable, integratable | Depends on vendor DPA | Self-hosted, REST API, open source |

---

## Hardware Notes

- **This demo** runs on a 48GB shared/partitioned AMD Instinct allocation provided for the hackathon (per AMD's official FAQ: *"About 48 GB... your model needs to be smaller"*).
- **Production deployments** target a dedicated single MI300X node with full 192GB HBM3, where the complete pipeline with a larger production model runs with significant headroom.
- **Note on hardware attestation:** "hardware-attested" AI (e.g. AMD SEV-SNP) requires kernel/hypervisor-level access not available in a hackathon sandbox. Enclave's audit chain and integrity manifest are honestly scoped as **software-level integrity verification** — the natural precursor to, and extension point toward, real SEV-SNP attestation in a production on-prem deployment.

---

## Quickstart

```bash
git clone https://github.com/KhanRayyan3622/enclave-ai
cd enclave-ai
pip install -r requirements.txt
cp .env.example .env  # add your Fireworks/Gemma keys, or point at local vLLM for prod

python test_pipeline.py          # run one full pipeline test
python -m dashboard.app          # launch the interactive dashboard
python api.py                    # launch the REST API on :8080
open landing/index.html          # view the landing page
```

### Docker (verified build)
```bash
docker build -t enclave-ai .
docker run -d -p 7860:7860 -p 8080:8080 --env-file .env --name enclave enclave-ai
curl http://localhost:7860 -I    # confirmed: HTTP/1.1 200 OK
```

### API examples
```bash
curl -X POST http://localhost:8080/review \
  -H "Content-Type: application/json" \
  -d '{"task": "Review this loan application: Income $65,000, Loan $450,000, DTI 42%, Credit Score 680, Employment 8 months."}'

curl -X POST http://localhost:8080/review/pdf -H "Content-Type: application/json" \
  -d '{"task": "..."}' --output evidence.pdf
```

---

## Tech stack

- **Inference:** ROCm 7.2 + vLLM 0.16 (AMD Instinct, verified on real hardware)
- **Agents:** Custom orchestration (Orchestrator → Researcher → Analyst → Auditor)
- **Dev/secondary backends:** Fireworks AI, Google Gemma API
- **Policy retrieval:** Local keyword-based RAG over `policies/` — zero external calls
- **API:** FastAPI + Uvicorn
- **PDF generation:** ReportLab
- **Dashboard:** Gradio, security-themed UI with live data-residency indicator
- **Deployment:** Docker (built and verified), single container

---

## Judging criteria fit

| Criterion | How Enclave addresses it |
|-----------|---------------------------|
| **Originality** | HBM capacity framed as a *compliance* enabler (network-topology argument), not just performance — paired with a full governance stack (citations, audit chain, EU AI Act mapping) no single-model demo offers |
| **Product/Market potential** | Named buyer (banks, hospitals, gov agencies), real regulatory pain (GDPR/HIPAA/EU AI Act Aug 2026), real AMD enterprise narrative already in market (Nebul, ConfidentialMind, Maincode) |
| **Completeness** | Full pipeline verified on real hardware, REST API, PDF export, batch processing, landing page, Docker build tested end-to-end |
| **Use of AMD platforms** | ROCm + vLLM + AMD Instinct's HBM capacity is the literal thesis, measured on actual AMD Developer Cloud infrastructure with real benchmark numbers |

---

## Project structure

```
enclave-ai/
├── agents/
│   ├── orchestrator.py, base_agent.py
│   ├── research_agent.py, analyst_agent.py, auditor_agent.py
│   ├── policy_retriever.py, framework_mapper.py
│   ├── audit_chain.py, integrity_manifest.py, sovereignty_score.py
│   ├── escalation.py, gemma_verifier.py, reaudit.py
│   ├── eu_ai_act_doc.py, evidence_package.py, flow_visualizer.py
│   └── batch_processor.py
├── autotuner/         # ROCm profiler + single-node-constrained config sweep
├── inference/          # Fireworks (dev) + vLLM local/AMD Cloud backends
├── dashboard/           # Gradio UI
├── landing/             # Static landing page
├── policies/             # Local policy corpus (fair lending, HIPAA, GDPR)
├── results/               # Real captured benchmark & audit data
├── sample_data/           # Batch processing test CSV
├── api.py                 # FastAPI REST service
├── Dockerfile, docker-compose.yml
└── test_pipeline.py
```

---

## License

MIT — open source, forkable, auditable (which matters a lot for a compliance product).
