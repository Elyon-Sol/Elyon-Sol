"""
Live attack-suite runner (docs/restructure/22_live_attack_run_and_real_transport_predicate_spec.md,
VL-083, C3-live). AUTHOR-EXECUTED on a real deployed surface - NOT run in the build sandbox or in
CI (no real surface exists here; it is excluded from the CI runner loop, parallel to the
multi-process-TLS / external-webhook skips).

This is the gate-1 referent external_verification_readiness.md names: the SAME VL-079 attack suite
the in-process runner defeats, run against a REAL gate + reference target over real cross-host
transport (TLS, via the C1/C2 deployment), so a green result is a real-attack result, not a
simulation. Configure it against the stood-up surface and run it:

    ELYON_LIVE_GATE_URL=https://gate.example:8000 \\
    ELYON_LIVE_TARGET_URL=https://target.example:9000 \\
    ELYON_LIVE_TARGET_ID=https://target.example:9000/target \\
    ELYON_TLS_CA_BUNDLE=/path/to/ca.crt \\
    PYTHONPATH=. python3 EVIDENCE/proofs/attack_suite_live_runner.py

Exits 0 iff the positive control is honored and every adversarial attack is DEFEATED over real
transport; exits 2 (loud) if unconfigured. On a green run, record C4: flip the REAL_TRANSPORT
predicate in EVIDENCE/readiness.json to green, naming this run's log as its proof.

SCOPE: the generic HTTP adapter cannot manipulate the gate's decision window or re-publish the
target's record, so the `stale` and `drifted_state` attacks are NOT driven here (they stay covered
by the in-process suite; the author may script those surface-state attacks separately). The live
run covers the request-tampering class over real transport: un-attested (A1), forged signature,
replay, rebind (tool / args), target_url swap, plus the positive control.
"""

import os
import sys

from EVIDENCE.proofs.attack_harness import HttpSurface, RequestsClient, run_suite

USAGE = (
    "unconfigured: set ELYON_LIVE_GATE_URL, ELYON_LIVE_TARGET_URL, ELYON_LIVE_TARGET_ID "
    "(and ELYON_TLS_CA_BUNDLE for real TLS, or leave unset for a public CA / plain HTTP). "
    "This runner is AUTHOR-executed against a real deployed surface; see the module docstring."
)


def main():
    gate_url = os.environ.get("ELYON_LIVE_GATE_URL")
    target_url = os.environ.get("ELYON_LIVE_TARGET_URL")
    target_id = os.environ.get("ELYON_LIVE_TARGET_ID")
    ca_bundle = os.environ.get("ELYON_TLS_CA_BUNDLE")
    if not (gate_url and target_url and target_id):
        print(USAGE)
        sys.exit(2)

    verify = ca_bundle if ca_bundle else True
    surface = HttpSurface(
        gate_client=RequestsClient(gate_url, verify=verify),
        target_client=RequestsClient(target_url, verify=verify),
        target_url=target_id,
    )

    print("=" * 92)
    print("LIVE ATTACK SUITE vs a REAL surface over real transport - VL-083 (C3-live)")
    print("  gate=%s  target=%s  target_id=%s  tls_ca=%s" % (
        gate_url, target_url, target_id, ca_bundle or "(system store / none)"))
    print("=" * 92)

    # include_stale=False / no drifted_surface: those are surface-state attacks the generic
    # adapter cannot drive over HTTP (see the module docstring).
    # The production gate uses PUSH delivery (VL-038): it forwards the admitted envelope to
    # the target on ELIGIBLE, so the honor is observed via the target acting, not by re-presenting.
    results = run_suite(surface, drifted_surface=None, include_stale=False, push_delivery=True)
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        outcome = "HONORED" if r.honored else ("REFUSED:" + r.reason)
        print("[%s] %-16s %-56s -> %s" % (verdict, r.id, r.challenge, outcome))

    print("-" * 92)
    defeated = sum(1 for r in results if r.passed and r.id != "positive_control")
    total = sum(1 for r in results if r.id != "positive_control")
    pos = next(r for r in results if r.id == "positive_control")
    print("positive control honored: %s | adversarial attacks defeated over real transport: %d/%d"
          % (pos.passed, defeated, total))
    ok = all(r.passed for r in results)
    print("=" * 92)
    print("RESULT:", "ALL ATTACKS DEFEATED over real transport (the gate-1 referent)" if ok
          else "AN ATTACK SUCCEEDED - do NOT flip REAL_TRANSPORT green")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
