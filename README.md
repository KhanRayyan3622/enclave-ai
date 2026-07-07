# 🔒 Enclave

> **The multi-agent AI system that never leaves the building.**  
> A sovereign, on-premise agentic AI pipeline that runs entirely inside a single AMD Instinct MI300X node — built for banks, hospitals, and government agencies that legally cannot send sensitive data to cloud APIs.

[![AMD MI300X](https://img.shields.io/badge/AMD-MI300X-ED1C24?style=flat)](https://www.amd.com/en/products/accelerators/instinct/mi300.html)
[![ROCm](https://img.shields.io/badge/ROCm-7.0-blue)](https://rocm.docs.amd.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## The problem

Regulated organizations — banks doing loan underwriting, hospitals processing intake forms, government agencies reviewing filings — want the productivity of agentic AI. But sending patient records, financial filings, or classified documents to OpenAI, Anthropic, or any cloud API is often a compliance violation before the first token is even generated. Data residency laws (GDPR, HIPAA, PCI-DSS, and sovereign-AI mandates across the EU, Gulf, and Asia) require sensitive data to never leave a controlled environment.

Most "on-prem AI" solutions solve this by running one small model on one small GPU — a fraction of what cloud-based agentic AI can do. That's the tradeoff Enclave removes.

## The solution

Enclave runs a complete 4-agent pipeline — Orchestrator, Researcher, Analyst, Auditor — entirely inside **one** AMD Instinct MI300X node. No data crosses a network boundary. No API call ever leaves the building.

This is only possible because of one specific hardware fact: **the MI300X has 192GB of HBM3 memory on a single GPU.** NVIDIA's H100 has 80GB. Fitting a multi-agent pipeline — four agent contexts, a shared KV-cache pool, and a production-size model — into one GPU is the difference between:

- **On MI300X:** one box, one power cord, zero network exposure, fully auditable
- **On H100:** 2-3 GPUs networked together to fit the same workload — every network hop between GPUs is an additional attack surface a compliance auditor has to sign off on

Enclave turns AMD's memory advantage into a literal compliance advantage.

---

## Architecture
┌──────────────────────────────────────────────────────────────────┐
│                    ENCLAVE — Single AMD MI300X Node                │
│                    (Air-gapped / VPC-isolated boundary)            │
│                                                                    │
│   Document/Task In ──▶ ┌─────────────────────┐                    │
│                        │  Orchestrator Agent │                    │
│                        │  (plans workflow,    │                    │
│                        │   never exports data)│                    │
│                        └──────────┬───────────┘                   │
│                                   │                                │
│              ┌────────────────────┼────────────────────┐          │
│              ▼                    ▼                    ▼          │
│     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│     │ Research Agent  │  │ Analyst Agent  │  │ Auditor Agent  │   │
│     │ (internal policy│  │ (extracts &    │  │ (compliance    │   │
│     │  & regulation    │  │  processes     │  │  verdict:      │   │
│     │  lookup)         │  │  document data)│  │  PASS/FLAG/FAIL)│  │
│     └────────┬────────┘  └───────┬────────┘  └───────┬────────┘   │
│              └────────────────────┼────────────────────┘          │
│                                   ▼                                │
│              ┌─────────────────────────────────────┐              │
│              │     Shared Inference Engine          │              │
│              │  vLLM + ROCm on MI300X (192GB HBM)  │              │
│              │  Shared KV-Cache Pool | Auto-Tuned   │              │
│              └─────────────────────────────────────┘              │
│                                                                    │
│         🔒 Result Out ── 0 bytes left this node ── 🔒              │
└──────────────────────────────────────────────────────────────────┘

## Agent roles

| Agent | Role |
|-------|------|
| **Orchestrator** | Receives the task, plans which agents handle what, coordinates execution — the only agent that "sees" the full task |
| **Researcher** | Retrieves relevant internal policy, regulation, or guideline context (RAG-style — from local/internal documents only) |
| **Analyst** | Extracts and processes the actual document data — fields, figures, entities — the core "reading" work |
| **Auditor** | Produces a final compliance verdict — PASS / FLAGGED / FAIL — with cited reasoning, the way a human compliance officer would sign off |

## Why this can't just be a cloud API

| | Cloud API (OpenAI/Anthropic/etc.) | Enclave on MI300X |
|---|---|---|
| Data leaves the building | ✅ Yes, every request | ❌ Never |
| Network hops for 4-agent workload | N/A (but data already left) | 0 — single node |
| GPUs needed for equivalent context | 2-3× H100 (80GB each) | 1× MI300X (192GB) |
| Auditable data flow | Depends on vendor DPA | Fully self-hosted, fully logged |
| Compliance with GDPR/HIPAA/data-sovereignty mandates | Requires vendor BAA/DPA | Native — data never transmitted |

---

## Quickstart

```bash
git clone https://github.com/YOUR_USERNAME/enclave-ai
cd enclave-ai
pip install -r requirements.txt
cp .env.example .env  # add your API key for dev, or point at local vLLM for prod

python test_pipeline.py
python -m dashboard.app
```

## Tech stack

- **Inference:** ROCm 7 + vLLM (AMD MI300X, single node)
- **Agents:** Custom orchestration (Orchestrator → Researcher → Analyst → Auditor)
- **Dev backend:** Fireworks AI (development/testing only — production runs entirely on AMD Developer Cloud MI300X)
- **Auto-tuner:** ROCm profiler-driven config sweep (tensor parallelism, KV-cache dtype, speculative decoding)
- **Dashboard:** Gradio, dark/security-themed UI with live data-residency indicator
- **Deployment:** Docker, single-container, no external dependencies at runtime

---

## Judging criteria fit

| Criterion | How Enclave addresses it |
|-----------|---------------------------|
| **Originality** | First hackathon submission framing MI300X's HBM capacity as a *compliance* enabler, not just a performance one |
| **Product/Market potential** | Named buyer (banks, hospitals, gov agencies), real regulatory pain (GDPR/HIPAA/sovereign AI mandates), real AMD enterprise narrative (Nebul, ConfidentialMind, Maincode all use MI300X for exactly this) |
| **Completeness** | Full working 4-agent pipeline, auto-tuner, dashboard, Dockerized |
| **Use of AMD platforms** | ROCm + vLLM + MI300X's HBM capacity is the literal thesis of the product, not an implementation detail |

---

## License

MIT — open source, forkable, auditable (which matters a lot for a compliance product).
