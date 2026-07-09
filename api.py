"""
Enclave REST API — wraps the multi-agent orchestrator as a callable
service, so external systems (e.g. a bank's loan origination software)
can integrate Enclave programmatically instead of only via the Gradio UI.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from inference.fireworks_client import get_client, DEFAULT_MODEL
from agents.orchestrator import OrchestratorAgent
from agents.evidence_package import generate_evidence_pdf

orchestrator_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator_instance
    client = get_client()
    orchestrator_instance = OrchestratorAgent(client=client, model=DEFAULT_MODEL)
    yield


app = FastAPI(
    title="Enclave API",
    description="Sovereign multi-agent compliance review — single-node, zero-egress.",
    version="1.0.0",
    lifespan=lifespan,
)


class ReviewRequest(BaseModel):
    task: str


class ReviewResponse(BaseModel):
    verdict: str
    sovereignty_score: float
    audit_chain_verified: bool
    integrity_manifest_hash: str
    frameworks_touched: list[str]
    escalation_required: bool
    auditor_reasoning: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Enclave", "data_residency": "0 bytes egress"}


@app.post("/review", response_model=ReviewResponse)
async def review(request: ReviewRequest):
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    result = await orchestrator_instance.execute(request.task)

    return ReviewResponse(
        verdict=result["verdict"],
        sovereignty_score=result["sovereignty_score"]["sovereignty_score"],
        audit_chain_verified=result["audit_chain_verified"],
        integrity_manifest_hash=result["integrity_manifest_hash"],
        frameworks_touched=result["framework_coverage"]["frameworks_touched"],
        escalation_required=result["escalation"] is not None,
        auditor_reasoning=result["results"]["auditor"]["result"],
    )


@app.post("/review/pdf")
async def review_pdf(request: ReviewRequest):
    """Same as /review but returns a downloadable PDF evidence package."""
    from fastapi.responses import FileResponse

    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    result = await orchestrator_instance.execute(request.task)
    path = generate_evidence_pdf(result)
    return FileResponse(path, media_type="application/pdf", filename="enclave_evidence_package.pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
