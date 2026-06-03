"""
VL-047 DEFAULT_SECURE cutover evidence runner (T-default-secure).

Demonstrates the mandatory signing cutover end to end in a single process:
pep.py's DEFAULT ELIGIBLE forward SIGNS the envelope; a co-located target
pinning the gate's public key HONORS the signed envelope and REFUSES an
unsigned forge; and a gate with NO signing key FAILS CLOSED
(REF_PEP_FAIL_CLOSED) rather than forward unsigned.

Cross-host transport is NOT exercised here (that is END_TO_END_NO_SHORTCUT /
G5, a separate readiness predicate); the verifying target is co-located and
uses verify_envelope's pinned-key + local-disk reassert path. The signing key
is a live Ed25519 keypair generated in-process; the private key is never
written to disk (the project-wide key custody rule).

The bound is unchanged: this closes forgery on what is now the only default
path, but the decisive failure (root / issuer key compromise, recovery
out-of-band) is unchanged, so "forgery-resistant" stays bounded and out of any
deposit.

Run from repo root:
  PYTHONPATH=. python3 EVIDENCE/proofs/default_secure_cutover_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.
"""

import json
import os
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.verifier import verify_envelope, ACCEPT_REASSERTED_AND_BOUND


TARGET = "http://127.0.0.1:9000/target"
KEY_ID = "gate-ed25519-cutover-001"


def _interaction():
    return {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }


def main():
    ok = True
    print("=" * 74)
    print("VL-047 DEFAULT_SECURE: the mandatory signing cutover, demonstrated")
    print("=" * 74)

    # Capture the gate's pushed header without a real network call.
    captured = {}

    class _Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None):
        captured["headers"] = headers or {}
        return _Resp()

    pep.requests.post = fake_post

    # ---- Signed default path: the gate has a key ----
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    pep._INJECTED_SIGNING_KEY = (priv, KEY_ID)

    interaction = _interaction()
    resp = TestClient(pep.app).post(
        "/governed-call",
        json={"target_url": TARGET, "interaction": interaction},
    )
    signed = json.loads(captured["headers"]["X-Elyon-Sol-Envelope"]) if captured else {}
    signed_ok = (
        resp.status_code == 200
        and signed.get("issuer_key_id") == KEY_ID
        and isinstance(signed.get("issuer_signature"), str)
    )
    print("[%s] default forward SIGNS the envelope" % ("PASS" if signed_ok else "FAIL"))
    ok = ok and signed_ok

    pinned = {KEY_ID: pub}
    accept = verify_envelope(signed, interaction, TARGET, pinned_public_keys=pinned)
    accept_ok = (
        accept["accepted"] is True
        and accept["reason"] == ACCEPT_REASSERTED_AND_BOUND
    )
    print("[%s] key-pinning target HONORS the signed envelope"
          % ("PASS" if accept_ok else "FAIL"))
    ok = ok and accept_ok

    forge = {k: v for k, v in signed.items() if k != "issuer_signature"}
    refuse = verify_envelope(forge, interaction, TARGET, pinned_public_keys=pinned)
    refuse_ok = refuse["accepted"] is False
    print("[%s] key-pinning target REFUSES the unsigned forge (reason=%s)"
          % ("PASS" if refuse_ok else "FAIL", refuse["reason"]))
    ok = ok and refuse_ok

    # ---- No-key path: the gate fails closed ----
    pep._INJECTED_SIGNING_KEY = None
    os.environ.pop("ELYON_SIGNING_KEY_HEX", None)
    os.environ.pop("ELYON_SIGNING_KEY_ID", None)
    resp2 = TestClient(pep.app).post(
        "/governed-call",
        json={"target_url": TARGET, "interaction": _interaction()},
    )
    nokey_ok = (
        resp2.status_code == 403
        and resp2.json()["detail"].get("refusal_reason_code") == "REF_PEP_FAIL_CLOSED"
    )
    print("[%s] no-key gate FAILS CLOSED (REF_PEP_FAIL_CLOSED, no downgrade)"
          % ("PASS" if nokey_ok else "FAIL"))
    ok = ok and nokey_ok

    print("-" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    print("Scope: DEFAULT_SECURE only (default forward signs + co-located verify).")
    print("Cross-host transport (END_TO_END_NO_SHORTCUT / G5) NOT asserted here.")
    print("'forgery-resistant' stays bounded (root/issuer compromise out-of-band).")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
