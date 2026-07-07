# Enclave — Sovereign Multi-Agent Compliance AI
# Designed to run entirely on a single AMD Instinct MI300X node.
FROM rocm/vllm:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 7860
EXPOSE 8000

# Enclave runs with zero required outbound network access at runtime
# (all inference is local to this container/node).
CMD ["python", "-m", "dashboard.app"]
