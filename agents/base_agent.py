import time
from openai import AsyncOpenAI


class BaseAgent:
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model
        self.name = "base"

    async def run(self, task: str) -> dict:
        raise NotImplementedError

    async def _call(self, system: str, user: str, max_tokens: int = 2000) -> dict:
        t0 = time.perf_counter()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.15,
            max_tokens=max_tokens,
        )
        latency_ms = (time.perf_counter() - t0) * 1000
        return {
            "result": response.choices[0].message.content,
            "tokens": response.usage.completion_tokens,
            "latency_ms": round(latency_ms, 1),
        }
