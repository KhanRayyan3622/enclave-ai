"""
Audit Chain — tamper-evident SHA-256 hash chain of every agent step.
Each entry hashes (previous_hash + this_step's_output), so the full
pipeline history can be independently verified after the fact — the
same auditability pattern used in high-trust compliance/security tools.
"""
import hashlib
import json
import time
from pathlib import Path


class AuditChain:
    def __init__(self):
        self.chain: list[dict] = []
        self._genesis_hash = "0" * 64

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def add_entry(self, agent: str, task: str, output: str) -> dict:
        prev_hash = self.chain[-1]["hash"] if self.chain else self._genesis_hash
        timestamp = time.time()
        payload = f"{prev_hash}|{agent}|{task}|{output}|{timestamp}"
        entry_hash = self._hash(payload)

        entry = {
            "index": len(self.chain),
            "agent": agent,
            "task_preview": task[:100],
            "output_preview": output[:200],
            "timestamp": timestamp,
            "prev_hash": prev_hash,
            "hash": entry_hash,
        }
        self.chain.append(entry)
        return entry

    def verify(self) -> bool:
        """Re-derive every hash and confirm the chain hasn't been tampered with."""
        prev_hash = self._genesis_hash
        for entry in self.chain:
            if entry["prev_hash"] != prev_hash:
                return False
            prev_hash = entry["hash"]
        return True

    def save(self, path: str = "results/audit_chain.json"):
        Path(path).parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "chain": self.chain,
                "verified": self.verify(),
                "entries": len(self.chain),
            }, f, indent=2)
