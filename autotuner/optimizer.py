from autotuner.config_sweep import ConfigSweeper


class InferenceOptimizer:
    def __init__(self, model: str):
        self.model = model
        self.sweeper = ConfigSweeper()

    async def find_optimal_config(self, budget_seconds: int = 20) -> dict:
        results = self.sweeper.sweep(budget_seconds=budget_seconds)
        best = results[0]

        print(f"\n[OPTIMIZER] Optimal single-node config:")
        print(f"  Batch Size: {best.config.max_num_batched_tokens}")
        print(f"  KV Cache: {best.config.kv_cache_dtype}")
        print(f"  Speculative Decode: {best.config.speculative_decoding}")
        print(f"  → {best.estimated_throughput_tps} tok/s, {best.estimated_memory_gb}GB, "
              f"fits on 1 node: {best.fits_single_node}")

        return {
            "max_num_batched_tokens": best.config.max_num_batched_tokens,
            "kv_cache_dtype": best.config.kv_cache_dtype,
            "speculative_decoding": best.config.speculative_decoding,
            "draft_model": best.config.draft_model,
            "estimated_throughput_tps": best.estimated_throughput_tps,
            "estimated_memory_gb": best.estimated_memory_gb,
            "fits_single_node": best.fits_single_node,
            "all_results": [
                {
                    "config": r.config.__dict__,
                    "throughput_tps": r.estimated_throughput_tps,
                    "memory_gb": r.estimated_memory_gb,
                    "fits_single_node": r.fits_single_node,
                    "score": r.score,
                }
                for r in results
            ]
        }
