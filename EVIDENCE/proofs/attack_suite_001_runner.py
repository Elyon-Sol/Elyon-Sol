"""
Attack suite runner (docs/restructure/19_attack_harness_and_claim_sheet_spec.md, VL-079, C3).

Runs the gate-2 break-it challenges (EVIDENCE/proofs/attack_harness.py) against the IN-PROCESS
surface and reports pass/fail per attack. An attack PASSES when it is DEFEATED (the gate refuses
with the expected reason); the positive control passes when the valid call is honored.

HONEST SCOPE (gate 2 / external_verification_readiness.md): a green run here proves the attacks
are well-formed and the gate refuses them on the in-process surface; it is NOT external
validation. The identical suite runs against a real cross-host surface (HttpSurface) once gate 1
(C1/C2 real transport) exists - that run, on real hosts, is the author's and is the referent that
external readiness actually needs. No result here moves that axis.

Run:  PYTHONPATH=. python3 EVIDENCE/proofs/attack_suite_001_runner.py
Exits 0 iff every attack is defeated and the positive control is honored.
"""

import json
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from EVIDENCE.proofs.attack_harness import InProcessSurface, run_suite

TARGET_ID = "mcp://elyon-sol/tool-server"
GATE_KID = "gate-attack-suite-001"
AUTHENTIC = "EVIDENCE/published_hashes.json"


def main():
    priv = Ed25519PrivateKey.generate()
    authentic = open(AUTHENTIC, "rb").read()
    drifted = json.dumps(
        {**json.loads(authentic), "evaluator_sha256": "0" * 64}, sort_keys=True
    ).encode("utf-8")

    surface = InProcessSurface(
        target_id=TARGET_ID, record_bytes=authentic,
        gate_key_id=GATE_KID, gate_private_key=priv,
    )
    drifted_surface = InProcessSurface(
        target_id=TARGET_ID, record_bytes=drifted,
        gate_key_id=GATE_KID, gate_public_key=priv.public_key(),
    )

    print("=" * 90)
    print("ATTACK SUITE (gate-2 falsifiable claims) vs the IN-PROCESS surface - VL-079 (C3)")
    print("=" * 90)

    results = run_suite(surface, drifted_surface=drifted_surface)
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        outcome = "HONORED" if r.honored else ("REFUSED:" + r.reason)
        print("[%s] %-16s %-56s -> %s" % (verdict, r.id, r.challenge, outcome))

    print("-" * 90)
    defeated = sum(1 for r in results if r.passed and r.id != "positive_control")
    total_attacks = sum(1 for r in results if r.id != "positive_control")
    pos = next(r for r in results if r.id == "positive_control")
    print("positive control honored: %s | adversarial attacks defeated: %d/%d"
          % (pos.passed, defeated, total_attacks))
    ok = all(r.passed for r in results)
    print("=" * 90)
    print("RESULT:", "ALL ATTACKS DEFEATED on the in-process surface (referent-incomplete until "
          "real transport - gate 1)" if ok else "AN ATTACK SUCCEEDED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
