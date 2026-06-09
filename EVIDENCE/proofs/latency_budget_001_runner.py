"""
Latency budget harness (docs/restructure/18_latency_budget_and_sdk_spec.md, increment VL-078, B5).

Measures the per-call latency Elyon-Sol adds, over N iterations on a warm keypair + record:
  - ADMIT path: pep end-to-end sign of one decision (the gate's per-call cost).
  - VERIFY path: ExecutorGate.check on a valid envelope (the executor's added per-call cost) -
    the number that matters for an integrator's tail latency.
Reports p50 / p95 / p99 / mean (ms) and throughput (calls/sec) for each.

HONEST SCOPE (locus AUTHOR for the numbers): the sandbox is shared / virtualized, so these
timings are INDICATIVE, not the budget of record. The harness is the SANDBOX deliverable; the
author re-runs it on representative hardware for the recorded budget. It measures in-process
verify cost only - NOT network / TLS cost (the G5 / Phase-C surface). The run applies only a
LOOSE regression sanity bound (not a budget): it fails only if it cannot collect samples or if
p50 verify exceeds a generous ceiling a non-pathological machine clears by orders of magnitude.

Run:  PYTHONPATH=. python3 EVIDENCE/proofs/latency_budget_001_runner.py [N]
Exits 0 iff the measurement completes and the loose sanity bound holds.
"""

import sys
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.executor_sdk import ExecutorGate
from IMPLEMENTATION.mcp_server import interaction_for

TARGET_ID = "mcp://elyon-sol/tool-server"
GATE_KID = "gate-latency-001"
TOOL = "transfer_funds"
ARGS = {"amount": 100, "to": "acct-42"}

# Loose regression sanity ceiling (NOT a budget). An Ed25519 sign/verify + a couple of
# SHA-256s is sub-millisecond on real hardware; 50 ms p50 catches only pathological regressions.
SANITY_P50_VERIFY_MS = 50.0


def _percentile(sorted_ms, q):
    if not sorted_ms:
        return float("nan")
    idx = min(len(sorted_ms) - 1, int(round(q * (len(sorted_ms) - 1))))
    return sorted_ms[idx]


def _summary(name, samples_ms):
    s = sorted(samples_ms)
    total_s = sum(samples_ms) / 1000.0
    tput = (len(samples_ms) / total_s) if total_s > 0 else float("inf")
    return {
        "name": name, "n": len(s),
        "p50": _percentile(s, 0.50), "p95": _percentile(s, 0.95),
        "p99": _percentile(s, 0.99), "mean": sum(s) / len(s),
        "min": s[0], "max": s[-1], "tput": tput,
    }


def _print_row(r):
    print("%-8s n=%-6d p50=%7.3f  p95=%7.3f  p99=%7.3f  mean=%7.3f  min=%7.3f  max=%8.3f  "
          "tput=%10.1f/s" % (r["name"], r["n"], r["p50"], r["p95"], r["p99"], r["mean"],
                             r["min"], r["max"], r["tput"]))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

    priv = Ed25519PrivateKey.generate()
    pep._INJECTED_SIGNING_KEY = (priv, GATE_KID)

    class _R:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        return _R()

    pep.requests.post = fake_post
    client = TestClient(pep.app)
    interaction = interaction_for(TOOL, ARGS)
    payload = {"target_url": TARGET_ID, "interaction": interaction}

    def admit_once():
        return client.post("/governed-call", json=payload).json()["envelope"]

    record_bytes = open("EVIDENCE/published_hashes.json", "rb").read()

    print("=" * 96)
    print("LATENCY BUDGET: Elyon-Sol per-call cost (VL-078, B5) - INDICATIVE sandbox figures")
    print("=" * 96)

    # Warm up (JIT/import/cache effects).
    for _ in range(50):
        admit_once()
    warm_env = admit_once()
    # A fresh-cache gate per verify sample so the replay cache never refuses (each verify is a
    # first-sight admit-shaped decision); measures the verify path cost, not replay growth.
    _g = ExecutorGate(pinned_public_keys={GATE_KID: priv.public_key()},
                      target_id=TARGET_ID, record_bytes=record_bytes)
    for _ in range(50):
        ExecutorGate(pinned_public_keys={GATE_KID: priv.public_key()},
                     target_id=TARGET_ID, record_bytes=record_bytes).check(warm_env, interaction)

    admit_ms = []
    for _ in range(n):
        t0 = time.perf_counter()
        admit_once()
        admit_ms.append((time.perf_counter() - t0) * 1000.0)

    verify_ms = []
    envs = [admit_once() for _ in range(n)]
    for env in envs:
        gate = ExecutorGate(pinned_public_keys={GATE_KID: priv.public_key()},
                            target_id=TARGET_ID, record_bytes=record_bytes)
        t0 = time.perf_counter()
        d = gate.check(env, interaction)
        verify_ms.append((time.perf_counter() - t0) * 1000.0)
        assert d.honored, d

    admit = _summary("ADMIT", admit_ms)
    verify = _summary("VERIFY", verify_ms)
    print("(milliseconds per call)")
    _print_row(admit)
    _print_row(verify)
    print("-" * 96)
    print("VERIFY is the executor's added per-call latency (the integrator-relevant tail).")
    print("Sanity ceiling (loose, not a budget): p50 VERIFY < %.1f ms -> %s (%.3f ms)" % (
        SANITY_P50_VERIFY_MS, "OK" if verify["p50"] < SANITY_P50_VERIFY_MS else "REGRESSION",
        verify["p50"]))
    print("NOTE: indicative sandbox figures; author re-runs on representative hardware for the "
          "budget of record. Network / TLS cost is NOT included (Phase C).")
    print("=" * 96)

    ok = (verify["n"] == n and admit["n"] == n and verify["p50"] < SANITY_P50_VERIFY_MS)
    print("RESULT:", "MEASURED" if ok else "SANITY BOUND EXCEEDED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
