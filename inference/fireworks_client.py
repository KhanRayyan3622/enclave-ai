"""
Dev inference backend (Fireworks AI). 
Production Enclave deployments point this at an on-prem vLLM server
running locally on the AMD MI300X node — see VLLM_BASE_URL in .env.
No code changes needed to swap; only the base_url changes.
"""
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1"),
        api_key=os.getenv("FIREWORKS_API_KEY"),
    )

DEFAULT_MODEL = "accounts/fireworks/models/deepseek-v4-pro"
