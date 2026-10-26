# Developer & Utility Scripts (`scripts/`)

This directory houses development utilities, benchmarking tools, demo generators, and synchronization scripts.

## 📜 Key Scripts

- [`benchmark_kv_cache.py`](benchmark_kv_cache.py) — Benchmarks KV cache latency, token throughput, and TTFT across supported model providers.
- [`generate_demo_gif.py`](generate_demo_gif.py) — Programmatically captures and compiles terminal walkthroughs into high-fidelity animated demo GIFs.
- [`sync_version.py`](sync_version.py) — Enforces synchronized semantic versioning across `pyproject.toml`, documentation, and manifest files.
- [`sync_to_public.py`](sync_to_public.py) — Default-deny allowlist synchronizer enforcing Phase 0/1 security and privacy barriers.
- [`sync_privacy_secret.py`](sync_privacy_secret.py) — Manages privacy pattern detection and local secret environment mapping.
- [`gto_exec.sh`](gto_exec.sh) — Shell wrapper executing GTO decision screening and risk audit routines.

## 🚀 Execution

All scripts are executable via Python 3:

```bash
python3 scripts/sync_version.py --check
```
