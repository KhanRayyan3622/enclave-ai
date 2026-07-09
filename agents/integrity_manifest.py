"""
Node Integrity Manifest — software-level state attestation.

IMPORTANT HONESTY NOTE: this is NOT hardware-level TEE attestation
(e.g. AMD SEV-SNP, which requires kernel/hypervisor access we don't have
in this environment). This is a software-level integrity manifest:
a signed, hashable record of exactly what code, model, and policy
corpus produced a given decision — the natural precursor to, and
extension point toward, real SEV-SNP attestation in a production
on-prem deployment.
"""
import hashlib
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone


class IntegrityManifest:
    def __init__(self, model_name: str, policy_dir: str = "policies"):
        self.model_name = model_name
        self.policy_dir = Path(policy_dir)

    def _hash_file(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

    def _hash_dir(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return {
            f.name: self._hash_file(f)
            for f in sorted(path.glob("*.md"))
        }

    def _get_rocm_version(self) -> str:
        try:
            result = subprocess.run(
                ["rocm-smi", "--version"], capture_output=True, text=True, timeout=3
            )
            return result.stdout.strip().split("\n")[0] if result.stdout else "not detected (dev backend)"
        except Exception:
            return "not detected (dev backend)"

    def generate(self, decision_hash: str) -> dict:
        """Generate the manifest for a completed pipeline decision."""
        manifest = {
            "manifest_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "node": {
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "rocm_version": self._get_rocm_version(),
            },
            "model": {
                "name": self.model_name,
            },
            "policy_corpus_hashes": self._hash_dir(self.policy_dir),
            "decision_hash": decision_hash,
            "attestation_level": "software-integrity (SHA-256 manifest)",
            "attestation_note": (
                "This manifest cryptographically records the exact model, "
                "policy corpus, and node state used for this decision. "
                "It does NOT constitute hardware-level TEE attestation "
                "(e.g. AMD SEV-SNP). In a production on-prem deployment, "
                "this manifest generation step would be extended to "
                "include a SEV-SNP attestation report from the AMD Secure "
                "Processor, cryptographically proving the underlying "
                "hardware and firmware state as well as the software state."
            ),
        }
        manifest_json = json.dumps(manifest, sort_keys=True)
        manifest["manifest_hash"] = hashlib.sha256(manifest_json.encode()).hexdigest()
        return manifest

    def save(self, manifest: dict, path: str = "results/integrity_manifest.json"):
        Path(path).parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)
