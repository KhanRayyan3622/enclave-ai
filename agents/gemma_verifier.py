"""
Gemma Verifier — lightweight second-opinion check on the Auditor's verdict,
using Google's Gemma model. Demonstrates real AMD-hosted Gemma usage
(Gemma is optimized for and commonly deployed on AMD Instinct GPUs via
ROCm/vLLM in production; here we call it via Google AI Studio's API
during hackathon development, with the same swap-the-endpoint pattern
used elsewhere in Enclave to move to local vLLM+Gemma-on-MI300X in
production).
"""
import os
import httpx


async def gemma_second_opinion(verdict: str, reasoning_summary: str) -> dict:
    """
    Ask Gemma: does this verdict look internally consistent given the
    reasoning provided? A lightweight sanity-check layer, not a
    replacement for the Auditor's full reasoning.
    """
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        return {
            "checked": False,
            "reason": "GOOGLE_AI_API_KEY not set — skipping Gemma second-opinion check",
        }

    prompt = f"""A compliance system produced this verdict: {verdict}

Based on this reasoning summary:
{reasoning_summary[:800]}

In one sentence, does this verdict look internally consistent with the reasoning given? Answer "CONSISTENT" or "INCONSISTENT" followed by a brief reason."""

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent?key={api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "checked": True,
                "model": "gemma-4-26b-a4b-it",
                "response": text.strip(),
            }
    except Exception as e:
        return {"checked": False, "reason": f"Gemma check failed: {e}"}
