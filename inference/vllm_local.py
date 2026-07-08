"""
Real vLLM server on AMD MI300X (production backend for Enclave).
Replaces Fireworks AI dev backend seamlessly.
"""
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_client() -> AsyncOpenAI:
    # On AMD Developer Cloud Jupyter: your vLLM server runs on localhost:8000
    # In production: point this at your on-prem MI300X node
    return AsyncOpenAI(
        base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
        api_key=os.getenv("VLLM_API_KEY", "abc-123"),
    )

# Use smaller model for 48GB allocation (FAQ said ~48GB available)
DEFAULT_MODEL = "Qwen/Qwen2-7B-Instruct"
