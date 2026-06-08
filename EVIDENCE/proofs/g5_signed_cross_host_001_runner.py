"""
Signed cross-host transport evidence runner (VL-048, T-end-to-end).

The no-shortcut proof of record for the END_TO_END_NO_SHORTCUT deployment
predicate (docs/restructure/10_readiness_spec.md section 4.2). It composes the
VL-047 mandatory signing cutover (the gate's DEFAULT forward signs) with the
VL-039 cross-host transport (a target on a separate process fetches the
published record over a real socket and checks currency against the FETCHED
record, not local disk) into a single chain with NO test-only shortcut:

  caller -> gate (signs on the DEFAULT path via the PRODUCTION key path)
         -> push (X-Elyon-Sol-Envelope header)
         -> TRANSPORT (real loopback socket; production fetch_published_record)
         -> target (separate process, genuinely divergent disk; pins the gate
            public key OUT-OF-BAND; verifies signature AND currency-from-record)
         -> honor / refuse.

What makes this no-shortcut (the four forbidden shortcuts of section 4.2, each
avoided here):

  - NOT a hand-built envelope: the envelope is produced by the real
    IMPLEMENTATION/pep.py /governed-call path and signed by pep._get_signing_key.
  - NOT in-process key injection: the gate resolves its signing key through the
    PRODUCTION path (the ELYON_SIGNING_KEY_HEX + ELYON_SIGNING_KEY_ID environment
    pair), exactly as a deployed gate would; the autouse conftest fixture (which
    monkeypatches _get_signing_key in-process) is explicitly NOT used - this
    runner is not a pytest test and imports no conftest.
  - NOT a loopback STUB: the published record crosses a real http.server socket
    via the production IMPLEMENTATION.published_source.fetch_published_record
    (a real requests.get); nothing on the fetch boundary is monkeypatched.
  - NOT a target importing gate internals: the target is a SUBPROCESS whose
    working tree is a copy of the repo with IMPLEMENTATION/evaluator.py
    byte-mutated, so its local evaluator hash genuinely differs from the gate's;
    it imports only the verifier + the transport reader, holds the gate public
    key as out-of-band configuration, and never imports pep.py.

Capabilities exercised end-to-end over transport (the END_TO_END_NO_SHORTCUT
dependency set per readiness.json + 10_readiness_spec.md section 4.2):
issuer_signing (the gate signs; the target verifies the signature against the
out-of-band-pinned public key) and enforcement_push (the envelope is delivered
as the attestation header and the target verifies it). issuer_key_expiry,
issuer_key_revocation, and root_rotation are NOT exercised here - they are not
on the default signed chain (expiry: the default forward stamps no not_after;
revocation/rotation: target-side record posture, ROOT_RECOVERY's territory).

The load-bearing result: the target HONORS the genuinely gate-signed, current,
bound envelope DESPITE its own divergent local disk (because it trusts the
fetched record for currency and the out-of-band pin for the signature), and
REFUSES the VL-039-follow-up-2 keyless forge (no signature -> the signed path
rejects it), a tampered envelope, a fetched record that fails the pinned anchor,
and an absent envelope.

Honest bound (carried from g5_cross_host_001.md's Decision G + the A3b finding):
greening END_TO_END_NO_SHORTCUT means the full signed chain runs over real
transport with no shortcut. It does NOT mean "deployed across real production
hosts" (true multi-machine + TLS is the named G5 floor, Decision F) and it does
NOT close the A3b freshness sub-class: a STALE-but-anchor-matching, validly
SIGNED record is still honored (reassert checks repo-state currency against the
record, not request liveness). forgery-resistant stays bounded
(signed-path-under-uncompromised-root) and out of any deposit.

Run from repo root:  PYTHONPATH=. python3 EVIDENCE/proofs/g5_signed_cross_host_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.

Ledger: VL-048 (T-end-to-end; signed cross-host chain, END_TO_END_NO_SHORTCUT).
"""

import base64
import hashlib
import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient

from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256

REPO = os.getcwd()
TARGET_URL = "http://127.0.0.1:9000/target"
PUBLISHED_PATH = os.path.join(REPO, "EVIDENCE", "published_hashes.json")
GATE_KEY_ID = "gate-signed-cross-host-001"


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


# The TARGET runs in a SUBPROCESS over a genuinely-divergent working tree. It
# fetches the published record over the real socket (production fetch path),
# pins the gate public key OUT-OF-BAND (passed in as base64, reconstructed
# locally), and verifies the SIGNED envelope against both the pinned key and
# the fetched record. It imports verifier + transport reader + envelope key
# reconstruction only; it never imports pep.py.
TARGET_DRIVER = '''\
import base64, json, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from IMPLEMENTATION.published_source import fetch_published_record
from IMPLEMENTATION.verifier import verify_envelope
from IMPLEMENTATION.envelope import _evaluator_sha256

inp = json.load(open(sys.argv[1]))
out = {"local_evaluator_sha256": _evaluator_sha256()}

# Out-of-band pinned gate public key (base64 raw Ed25519), reconstructed here.
pinned = None
if inp.get("gate_pub_b64") is not None:
    raw = base64.b64decode(inp["gate_pub_b64"])
    pinned = {inp["gate_key_id"]: Ed25519PublicKey.from_public_bytes(raw)}

# Real transport: fetch the published record over the socket, anchor-verify it.
record = fetch_published_record(inp["publisher_url"], inp["pinned_root"])
if record is None:
    out.update(honored=False, reason="REF_TARGET_ANCHOR_MISMATCH",
               local_disk_contrast_reason="n/a")
    print(json.dumps(out)); sys.exit(0)

env = inp["envelope"]
res = verify_envelope(env, inp["interaction"], inp["target_url"],
                      record_source=record, pinned_public_keys=pinned)
# Contrast: the same envelope verified against LOCAL disk (no record_source)
# on this divergent tree - shows a VL-038-style verify would have refused.
contrast = (verify_envelope(env, inp["interaction"], inp["target_url"],
                            pinned_public_keys=pinned)["reason"]
            if env is not None else "n/a")
out.update(honored=res["accepted"], reason=res["reason"],
           local_disk_contrast_reason=contrast)
print(json.dumps(out))
'''


def _gate_sign_via_production_path(interaction, target_url, priv, key_id):
    """
    Drive the real pep.py /governed-call ELIGIBLE path with the gate's signing
    key resolved through the PRODUCTION env-var path (ELYON_SIGNING_KEY_HEX +
    ELYON_SIGNING_KEY_ID), NOT the conftest in-process fixture. Capture the
    pushed signed envelope from the X-Elyon-Sol-Envelope header.

    pep._get_signing_key() reads the env pair and constructs an
    Ed25519PrivateKey; this is exactly the deployed-gate key path. We set the
    env, import pep fresh, and replace only requests.post (the UPSTREAM hop) so
    nothing leaves the process - that is the forward to the target, which is the
    next hop we drive explicitly, not a shortcut on the signing/transport path
    under test.
    """
    key_hex = priv.private_bytes_raw().hex() if hasattr(priv, "private_bytes_raw") else None
    if key_hex is None:
        from cryptography.hazmat.primitives.serialization import (
            Encoding as _E, PrivateFormat as _PF, NoEncryption as _NE,
        )
        key_hex = priv.private_bytes(_E.Raw, _PF.Raw, _NE()).hex()

    os.environ["ELYON_SIGNING_KEY_HEX"] = key_hex
    os.environ["ELYON_SIGNING_KEY_ID"] = key_id

    import IMPLEMENTATION.pep as pep_module

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

    if resp.status_code != 200:
        raise RuntimeError("gate did not return ELIGIBLE: %d %s"
                           % (resp.status_code, resp.text))
    header = captured["headers"].get("X-Elyon-Sol-Envelope")
    if header is None:
        raise RuntimeError("gate did not push X-Elyon-Sol-Envelope header")
    return json.loads(header)


def main():
    authentic_bytes = open(PUBLISHED_PATH, "rb").read()
    pinned_root = anchor_sha256(authentic_bytes)
    authentic_eval = hashlib.sha256(
        open(os.path.join(REPO, "IMPLEMENTATION", "evaluator.py"), "rb").read()
    ).hexdigest()

    # The gate's signing keypair, generated live; private half never persisted,
    # passed to pep ONLY via the env-var production path; public half pinned to
    # the target out-of-band (as base64).
    gate_priv = Ed25519PrivateKey.generate()
    gate_pub_b64 = base64.b64encode(
        gate_priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    ).decode("ascii")

    interaction = {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": manifest_sha256(),
    }

    # Gate signs on the DEFAULT path via the production key path.
    signed_env = _gate_sign_via_production_path(
        interaction, TARGET_URL, gate_priv, GATE_KEY_ID
    )
    # The VL-039-follow-up-2 keyless forge: strip the signature (the adversary
    # holds no key). The signed path must refuse this.
    forge_env = {k: v for k, v in signed_env.items() if k != "issuer_signature"}
    # A tampered signed envelope: mutate request_context without re-signing.
    tampered_env = json.loads(json.dumps(signed_env))
    tampered_env["request_context"]["AP"] = ["identity", "role", "admin"]

    # Publishers: authentic and tampered (different bytes -> fails pinned anchor).
    auth_url, auth_httpd = _serve(authentic_bytes)
    tampered_bytes = authentic_bytes.replace(b"0.9.8.4", b"6.6.6.6")
    tamp_url, tamp_httpd = _serve(tampered_bytes)

    # TARGET tree: a genuinely mutated copy (evaluator.py differs from the gate).
    tdir = tempfile.mkdtemp(prefix="g5_signed_target_")
    for sub in ("IMPLEMENTATION", "CANON", "MANIFEST", "EVIDENCE"):
        shutil.copytree(os.path.join(REPO, sub), os.path.join(tdir, sub))
    eval_path = os.path.join(tdir, "IMPLEMENTATION", "evaluator.py")
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write("\n# VL-048 signed-cross-host demo: divergent target tree\n")
    target_eval = hashlib.sha256(open(eval_path, "rb").read()).hexdigest()
    open(os.path.join(tdir, "target_driver.py"), "w", encoding="utf-8").write(TARGET_DRIVER)

    assert target_eval != authentic_eval, "target tree must genuinely differ"

    def run_target(envelope, publisher_url, gate_pub_b64_arg):
        payload = {
            "envelope": envelope, "interaction": interaction,
            "target_url": TARGET_URL, "publisher_url": publisher_url,
            "pinned_root": pinned_root,
            "gate_pub_b64": gate_pub_b64_arg, "gate_key_id": GATE_KEY_ID,
        }
        fpath = os.path.join(tdir, "case.json")
        json.dump(payload, open(fpath, "w"))
        env = dict(os.environ, PYTHONPATH=tdir)
        # The target subprocess must NOT inherit the gate's signing key env -
        # it verifies with the out-of-band public pin only.
        env.pop("ELYON_SIGNING_KEY_HEX", None)
        env.pop("ELYON_SIGNING_KEY_ID", None)
        r = subprocess.run(
            [sys.executable, os.path.join(tdir, "target_driver.py"), fpath],
            cwd=tdir, env=env, capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise RuntimeError("target subprocess failed: " + r.stderr)
        return json.loads(r.stdout.strip())

    print("=" * 74)
    print("G5 SIGNED cross-host transport demonstration (VL-048)")
    print("=" * 74)
    print("Pinned anchor (sha256 of EVIDENCE/published_hashes.json): %s" % pinned_root)
    print("Gate evaluator sha256   : %s" % authentic_eval)
    print("TARGET local evaluator  : %s  <- genuinely divergent" % target_eval)
    print("Gate signing key_id     : %s  (resolved via ELYON_SIGNING_KEY_* env)" % GATE_KEY_ID)
    print("Gate public key (pinned out-of-band, b64): %s" % gate_pub_b64)
    print("Publisher (authentic)   : %s" % auth_url)
    print("Publisher (tampered)    : %s" % tamp_url)
    print("-" * 74)

    cases = [
        ("signed valid, authentic record (DIVERGENT target disk)",
         signed_env, auth_url, gate_pub_b64, True, "REASSERTED_AND_BOUND"),
        ("keyless forge (no signature), authentic record",
         forge_env, auth_url, gate_pub_b64, False, "REF_VERIFY_SIGNATURE_INVALID"),
        ("tampered signed envelope, authentic record",
         tampered_env, auth_url, gate_pub_b64, False, "REF_VERIFY_SIGNATURE_INVALID"),
        ("signed valid, tampered record (fails pinned anchor)",
         signed_env, tamp_url, gate_pub_b64, False, "REF_TARGET_ANCHOR_MISMATCH"),
        ("no envelope (A1), authentic record",
         None, auth_url, gate_pub_b64, False, "REF_VERIFY_ENVELOPE_ABSENT"),
    ]

    ok = True
    results = []
    for label, env, purl, pub_arg, exp_honored, exp_reason in cases:
        v = run_target(env, purl, pub_arg)
        passed = (v["honored"] == exp_honored and v["reason"] == exp_reason)
        ok = ok and passed
        results.append((label, v, exp_honored, exp_reason, passed))
        print("[%s] %s" % ("PASS" if passed else "FAIL", label))
        print("       honored=%s reason=%s" % (v["honored"], v["reason"]))
        if v.get("local_disk_contrast_reason") not in (None, "n/a"):
            print("       (VL-038 local-disk verify on this divergent tree would have"
                  " returned: %s)" % v["local_disk_contrast_reason"])

    print("-" * 74)
    # Load-bearing invariant: the signed valid case was HONORED despite the
    # divergent disk, AND the local-disk contrast shows it would have refused.
    valid_v = results[0][1]
    killer = (valid_v["honored"] is True
              and valid_v["local_disk_contrast_reason"]
              == "REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED")
    print("KILLER PROPERTY (signed-honor-despite-divergent-disk + local-disk-would-refuse): %s"
          % ("HOLDS" if killer else "FAILED"))
    ok = ok and killer

    auth_httpd.shutdown(); tamp_httpd.shutdown()
    shutil.rmtree(tdir, ignore_errors=True)
    os.environ.pop("ELYON_SIGNING_KEY_HEX", None)
    os.environ.pop("ELYON_SIGNING_KEY_ID", None)

    print("=" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
