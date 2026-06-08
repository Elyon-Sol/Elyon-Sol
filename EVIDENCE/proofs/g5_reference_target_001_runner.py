"""
Reference enforcing-target evidence runner (VL-061, T-G5-transport;
docs/restructure/12_g5_transport_design.md step 4).

The no-shortcut proof of record for the artifact-12 step-4 deliverable: the
STANDALONE, DEPLOYABLE reference enforcing target (IMPLEMENTATION/reference_target.py)
honors a valid gate-signed routed call and refuses the forge / replay /
target_url-swap / absent-envelope / record-mismatch set, with:

  - the target configured ENTIRELY out-of-band through its real env-config path
    (config_from_env reads ELYON_TARGET_URL / ELYON_PUBLISHER_URL /
    ELYON_PINNED_ROOT_SHA256 / ELYON_GATE_KEY_ID / ELYON_GATE_PUBLIC_KEY_HEX) -
    no injected config; the same code path a deployer uses;
  - the published-record hop over a REAL loopback socket (a stdlib http.server
    publisher) via the production IMPLEMENTATION.published_source.fetch_published_record -
    nothing on the fetch boundary is monkeypatched;
  - the envelope produced and SIGNED by the real IMPLEMENTATION/pep.py
    /governed-call ELIGIBLE path with the gate key resolved through the
    PRODUCTION env path (ELYON_SIGNING_KEY_HEX + ELYON_SIGNING_KEY_ID), NOT the
    conftest in-process fixture (this runner is not a pytest test and imports no
    conftest);
  - the gate's signing PUBLIC key pinned to the target out-of-band as hex.

What this is and is not (the two finish lines, artifact 12 section 1): this
greens finish line (A) for step 4 - a deployable reference target exercised over
the current loopback transport. It is NOT finish line (B): real cross-host TLS
transport is artifact 12 steps 2-3, and G5 CLOSED requires an EXTERNAL attacker
(per GR-3 every attack here is characterization, not certification). The
gate-to-target hop is modeled (the signed envelope captured from pep's push and
re-delivered to the target) exactly as the prior cross-host runners do; promoting
that hop to a real socket + TLS is steps 2-3, not step 4.

The reference target is NOT authored-to-pass: its acceptance criterion is solely
"verify_envelope accepts against the anchor-verified fetched record AND the
pinned gate signature verifies"; it consults only its out-of-band pins and the
production verifier.

Run from repo root:  PYTHONPATH=. python3 EVIDENCE/proofs/g5_reference_target_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.

Ledger: VL-061 (T-G5-transport; artifact 12 step 4 reference enforcing target).
"""

import http.server
import os
import socketserver
import sys
import threading

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient

from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256

REPO = os.getcwd()
TARGET_URL = "http://127.0.0.1:9000/target"
OTHER_URL = "http://127.0.0.1:9000/other"
PUBLISHED_PATH = os.path.join(REPO, "EVIDENCE", "published_hashes.json")
GATE_KEY_ID = "gate-reference-target-001"


def _serve(record_bytes):
    """Start a loopback HTTP server serving record_bytes; return (url, httpd)."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(record_bytes)))
            self.end_headers()
            self.wfile.write(record_bytes)

        def log_message(self, *a):
            pass

    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d/published_hashes.json" % port, httpd


def _gate_sign_via_production_path(interaction, target_url, priv, key_id):
    """
    Drive the real pep.py /governed-call ELIGIBLE path with the gate's signing
    key resolved through the PRODUCTION env path (ELYON_SIGNING_KEY_HEX +
    ELYON_SIGNING_KEY_ID), NOT the conftest fixture. Return (signed_env, body)
    captured from the X-Elyon-Sol-Envelope push.
    """
    key_hex = priv.private_bytes_raw().hex()
    os.environ["ELYON_SIGNING_KEY_HEX"] = key_hex
    os.environ["ELYON_SIGNING_KEY_ID"] = key_id

    import IMPLEMENTATION.pep as pep_module
    import json as _json

    captured = {}

    class _Resp:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers or {}
        return _Resp()

    original = pep_module.requests.post
    pep_module.requests.post = fake_post
    try:
        client = TestClient(pep_module.app)
        resp = client.post(
            "/governed-call",
            json={"target_url": target_url, "interaction": interaction},
        )
    finally:
        pep_module.requests.post = original
        os.environ.pop("ELYON_SIGNING_KEY_HEX", None)
        os.environ.pop("ELYON_SIGNING_KEY_ID", None)

    if resp.status_code != 200:
        raise RuntimeError("gate did not return ELIGIBLE: %d %s"
                           % (resp.status_code, resp.text))
    header = captured["headers"].get("X-Elyon-Sol-Envelope")
    if header is None:
        raise RuntimeError("gate did not push X-Elyon-Sol-Envelope header")
    return _json.loads(header), captured["json"]


def main():
    authentic_bytes = open(PUBLISHED_PATH, "rb").read()
    pinned_root = anchor_sha256(authentic_bytes)
    tampered_bytes = authentic_bytes.replace(b"0.9.8.4", b"6.6.6.6")
    assert tampered_bytes != authentic_bytes

    auth_url, auth_httpd = _serve(authentic_bytes)
    tamp_url, tamp_httpd = _serve(tampered_bytes)

    # Gate signing keypair: private half passed to pep via the env production
    # path only; public half pinned to the target out-of-band (as hex).
    gate_priv = Ed25519PrivateKey.generate()
    gate_pub_hex = gate_priv.public_key().public_bytes(
        Encoding.Raw, PublicFormat.Raw
    ).hex()

    interaction = {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }
    interaction_y = {
        "AP": ["identity", "role", "admin"], "OP": ["session", "request"],
        "context": {}, "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }

    # Mint envelopes via the production signing path.
    signed_env, body = _gate_sign_via_production_path(
        interaction, TARGET_URL, gate_priv, GATE_KEY_ID
    )
    swap_env, _ = _gate_sign_via_production_path(
        interaction, OTHER_URL, gate_priv, GATE_KEY_ID
    )
    forge_env = {k: v for k, v in signed_env.items() if k != "issuer_signature"}

    # Configure the target ENTIRELY out-of-band via its real env-config path.
    os.environ["ELYON_TARGET_URL"] = TARGET_URL
    os.environ["ELYON_PUBLISHER_URL"] = auth_url
    os.environ["ELYON_PINNED_ROOT_SHA256"] = pinned_root
    os.environ["ELYON_GATE_KEY_ID"] = GATE_KEY_ID
    os.environ["ELYON_GATE_PUBLIC_KEY_HEX"] = gate_pub_hex

    # Import the DEPLOYABLE module-level app (config_from_env per request) and
    # the production fetch_published_record over the real socket - no injection.
    from IMPLEMENTATION.reference_target import app as target_app
    client = TestClient(target_app)

    def post(body_obj, envelope):
        headers = {}
        if envelope is not None:
            headers["X-Elyon-Sol-Envelope"] = canonical_json(envelope)
        r = client.post("/target", json=body_obj, headers=headers)
        if r.status_code == 200:
            return True, r.json().get("reason")
        return False, r.json().get("detail", {}).get("reason")

    print("=" * 74)
    print("G5 reference enforcing-target demonstration (VL-061, artifact 12 step 4)")
    print("=" * 74)
    print("Pinned anchor (sha256 of EVIDENCE/published_hashes.json): %s" % pinned_root)
    print("Gate signing key_id     : %s  (resolved via ELYON_SIGNING_KEY_* env)" % GATE_KEY_ID)
    print("Gate public key (pinned out-of-band, hex): %s" % gate_pub_hex)
    print("Target config           : via config_from_env (ELYON_TARGET_URL etc.)")
    print("Publisher (authentic)   : %s" % auth_url)
    print("Publisher (tampered)    : %s" % tamp_url)
    print("-" * 74)

    results = []

    def check(label, honored, reason, exp_honored, exp_reason):
        passed = (honored == exp_honored and reason == exp_reason)
        results.append(passed)
        print("[%s] %s" % ("PASS" if passed else "FAIL", label))
        print("       honored=%s reason=%s" % (honored, reason))

    # 1. signed valid, authentic record -> honored.
    h, r = post(body, signed_env)
    check("signed valid, authentic record", h, r, True, "REASSERTED_AND_BOUND")
    acted_once = (len(target_app.state.received) == 1)

    # 2. keyless forge (no signature) -> REF_VERIFY_SIGNATURE_INVALID.
    h, r = post(body, forge_env)
    check("keyless forge (no signature)", h, r, False, "REF_VERIFY_SIGNATURE_INVALID")

    # 3. replay / binding mismatch (envelope for X, body Y) -> binding mismatch.
    h, r = post(interaction_y, signed_env)
    check("replay: envelope for X, live interaction Y", h, r, False,
          "REF_VERIFY_BINDING_MISMATCH")

    # 4. target_url swap (envelope bound to /other) -> binding mismatch.
    h, r = post(body, swap_env)
    check("target_url swap (envelope bound to /other)", h, r, False,
          "REF_VERIFY_BINDING_MISMATCH")

    # 5. absent envelope (A1), authentic record -> REF_VERIFY_ENVELOPE_ABSENT.
    h, r = post(body, None)
    check("no envelope (A1), authentic record", h, r, False,
          "REF_VERIFY_ENVELOPE_ABSENT")

    # 6. record mismatch: point the target at the tampered publisher (the real
    #    env-config is re-read per request). fetch returns None -> anchor mismatch.
    os.environ["ELYON_PUBLISHER_URL"] = tamp_url
    h, r = post(body, signed_env)
    check("signed valid, tampered record (fails pinned anchor)", h, r, False,
          "REF_TARGET_ANCHOR_MISMATCH")
    os.environ["ELYON_PUBLISHER_URL"] = auth_url

    # 7. unconfigured -> fail closed (pop a required pin; restore after).
    os.environ.pop("ELYON_GATE_PUBLIC_KEY_HEX", None)
    h, r = post(body, signed_env)
    check("incomplete out-of-band config", h, r, False, "REF_TARGET_NOT_CONFIGURED")
    os.environ["ELYON_GATE_PUBLIC_KEY_HEX"] = gate_pub_hex

    print("-" * 74)
    print("ACTED EXACTLY ONCE (only the honored call): %s"
          % ("HOLDS" if acted_once and len(target_app.state.received) == 1 else "FAILED"))
    print("  (target.received len = %d; expected 1)" % len(target_app.state.received))

    ok = all(results) and acted_once and len(target_app.state.received) == 1

    auth_httpd.shutdown(); tamp_httpd.shutdown()
    for k in ("ELYON_TARGET_URL", "ELYON_PUBLISHER_URL", "ELYON_PINNED_ROOT_SHA256",
              "ELYON_GATE_KEY_ID", "ELYON_GATE_PUBLIC_KEY_HEX"):
        os.environ.pop(k, None)

    print("=" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
