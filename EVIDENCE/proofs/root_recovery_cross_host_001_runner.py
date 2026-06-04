"""
Root-recovery cross-host transport evidence runner (VL-049, T-root-recovery-wire).

The no-shortcut proof of record for the ROOT_RECOVERY deployment predicate
(docs/restructure/10_readiness_spec.md section 4 item 3). It extends the VL-048
signed cross-host chain (g5_signed_cross_host_001_runner.py) with the VL-044
planned-rotation + per-root-status mechanism, run over real transport with NO
test-only shortcut:

  caller -> gate (signs on the DEFAULT path via the PRODUCTION key path)
         -> push (X-Elyon-Sol-Envelope header)
         -> TRANSPORT (real loopback sockets; production fetch_published_record
            + fetch_root_record + fetch_key_record)
         -> target (separate process, genuinely divergent disk; pins ONLY R1
            OUT-OF-BAND and never re-pins; fetches the root record (R1 designates
            R2), builds the status view, fetches the key record (signed by the
            designated-active R2, vouching the gate's issuer key), validates it
            against the status view, then verifies the envelope's signature
            against the R2-vouched key AND currency-from-the-fetched-record AND
            binding)
         -> honor / refuse.

The KILLER PROPERTY: a target pinning ONLY R1, never re-pinned, HONORS a
gate-signed envelope whose issuer key is vouched by a key record signed by the
DESIGNATED-ACTIVE successor R2 - a planned in-band R1->R2 rotation with no
re-pin - DESPITE the target's own divergent local disk (currency comes from the
fetched published record, not local disk). It REFUSES the keyless forge, a key
record signed by a REVOKED root, a NEW key record signed by a RETIRED root, a
root-record fetch failure, and a stale root record.

What makes this no-shortcut (the four forbidden shortcuts of section 4.2, each
avoided here, exactly as VL-048):
  - NOT a hand-built envelope: produced by the real IMPLEMENTATION/pep.py
    /governed-call path and signed by pep._get_signing_key.
  - NOT in-process key injection: the gate resolves its signing key through the
    PRODUCTION path (ELYON_SIGNING_KEY_HEX + ELYON_SIGNING_KEY_ID); the autouse
    conftest fixture is NOT used (this is not a pytest test and imports no
    conftest).
  - NOT a loopback STUB: the published, root, and key records each cross a real
    http.server socket via the production
    IMPLEMENTATION.published_source.fetch_published_record /
    IMPLEMENTATION.root_record_source.fetch_root_record /
    IMPLEMENTATION.key_record_source.fetch_key_record (real requests.get);
    nothing on the fetch boundary is monkeypatched.
  - NOT a target importing gate internals: the target is a SUBPROCESS whose
    working tree is a copy of the repo with IMPLEMENTATION/evaluator.py
    byte-mutated, so its local evaluator hash genuinely differs from the gate's;
    it imports only the verifier + the three transport readers + the envelope
    key reconstruction, holds R1's public key as out-of-band configuration, and
    never imports pep.py.

Capabilities exercised end-to-end over transport (the ROOT_RECOVERY dependency
set per readiness.json + 10_readiness_spec.md section 4 item 3): root_rotation
(the target fetches the root record, builds the status view, and survives the
planned in-band R1->R2 rotation) and issuer_key_revocation (the key-record path
that lets R2 vouch the issuer key without a re-pin, and refuses a revoked/retired
root). issuer_signing + enforcement_push are also exercised (carried from
VL-048: the gate signs, the envelope is pushed and verified), but those flipped
at VL-048; ROOT_RECOVERY's enumerated set is the two new ones.

Honest bound (carried): greening ROOT_RECOVERY means a planned in-band R1->R2
rotation is consulted target-side on the signed chain over real transport with
no shortcut, and a revoked/retired root is refused. It does NOT close root-key
COMPROMISE recovery (irreducibly out-of-band, artifact 11 section 2, the named
non-goal), and it does NOT mean true multi-machine + TLS (the named G5 floor,
Decision F). forgery-resistant stays bounded (signed-path-under-uncompromised-
root) and out of any deposit.

Run from repo root:
  PYTHONPATH=. python3 EVIDENCE/proofs/root_recovery_cross_host_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.

Ledger: VL-049 (T-root-recovery-wire; ROOT_RECOVERY green, 3 of 3).
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
from datetime import datetime, timezone, timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256
from EVIDENCE.published_roots_gen import build_root_record, make_root_entry
from EVIDENCE.published_keys_gen import build_key_record, make_key_entry

REPO = os.getcwd()
TARGET_URL = "http://127.0.0.1:9000/target"
PUBLISHED_PATH = os.path.join(REPO, "EVIDENCE", "published_hashes.json")
GATE_KEY_ID = "gate-root-recovery-001"
R1_ID, R2_ID = "root-1", "root-2"


def _serve(record_bytes):
    """Start a loopback HTTP server serving record_bytes for any GET; return
    (url, httpd). A fresh ephemeral port per call."""
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
    return "http://127.0.0.1:%d/record.json" % port, httpd


# The TARGET runs in a SUBPROCESS over a genuinely-divergent working tree. It
# fetches the published record (currency), the root record (status view), and
# the key record (issuer-key trust) over REAL sockets via the production fetch
# functions, pins ONLY R1 out-of-band (passed in as base64, reconstructed
# locally), and verifies the SIGNED envelope against the R2-vouched key + the
# fetched currency record + binding. It imports verifier + the three readers +
# envelope key reconstruction only; it never imports pep.py.
TARGET_DRIVER = '''\
import base64, json, sys
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from IMPLEMENTATION.published_source import fetch_published_record
from IMPLEMENTATION.root_record_source import fetch_root_record
from IMPLEMENTATION.key_record_source import fetch_key_record
from IMPLEMENTATION.verifier import verify_envelope
from IMPLEMENTATION.envelope import _evaluator_sha256

inp = json.load(open(sys.argv[1]))
now = datetime.fromisoformat(inp["now"])
out = {"local_evaluator_sha256": _evaluator_sha256()}

# Out-of-band pinned ROOT key R1 (base64 raw Ed25519), reconstructed here.
# The target pins ONLY R1 and never re-pins.
r1_raw = base64.b64decode(inp["r1_pub_b64"])
pinned_roots = {inp["r1_id"]: Ed25519PublicKey.from_public_bytes(r1_raw)}

# Real transport 1: the published record (currency), anchor-verified.
record = fetch_published_record(inp["publisher_url"], inp["pinned_root_sha"])
if record is None:
    out.update(honored=False, reason="REF_TARGET_ANCHOR_MISMATCH")
    print(json.dumps(out)); sys.exit(0)

# Real transport 2: the root record -> per-root status view (R2 designated).
rv = fetch_root_record(inp["root_url"], pinned_roots, now=now)
if rv["reason"] is not None:
    # fail-closed: no validated status view -> refuse (do not honor).
    out.update(honored=False, reason=rv["reason"])
    print(json.dumps(out)); sys.exit(0)

# Real transport 3: the key record, validated against the status view (the
# VL-049 passthrough). A revoked/retired signing root is refused here.
kv = fetch_key_record(inp["key_url"], pinned_roots, now=now,
                      root_status_view=rv["status_view"])
if kv["reason"] is not None:
    out.update(honored=False, reason=kv["reason"])
    print(json.dumps(out)); sys.exit(0)

env = inp["envelope"]
res = verify_envelope(env, inp["interaction"], inp["target_url"],
                      record_source=record, key_record_view=kv["trust_view"],
                      now=now)
# Contrast: the same envelope verified against LOCAL disk (no record_source) on
# this divergent tree - shows a local-disk verify would have refused on currency.
contrast = (verify_envelope(env, inp["interaction"], inp["target_url"],
                            key_record_view=kv["trust_view"], now=now)["reason"]
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
    pushed signed envelope from the X-Elyon-Sol-Envelope header. Identical
    mechanism to the VL-048 runner (the signing path under test is the deployed
    one); only requests.post (the upstream hop) is replaced so nothing leaves
    the process - the next hop is the target we drive explicitly.
    """
    from cryptography.hazmat.primitives.serialization import (
        Encoding as _E, PrivateFormat as _PF, NoEncryption as _NE,
    )
    if hasattr(priv, "private_bytes_raw"):
        key_hex = priv.private_bytes_raw().hex()
    else:
        key_hex = priv.private_bytes(_E.Raw, _PF.Raw, _NE()).hex()

    os.environ["ELYON_SIGNING_KEY_HEX"] = key_hex
    os.environ["ELYON_SIGNING_KEY_ID"] = key_id

    from fastapi.testclient import TestClient
    import IMPLEMENTATION.pep as pep_module

    captured = {}

    class _Resp:
        status_code = 200
        text = '{"ok": true}'

    def fake_post(url, json, timeout, headers=None):
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
    now = datetime.now(timezone.utc)
    authentic_bytes = open(PUBLISHED_PATH, "rb").read()
    pinned_root_sha = anchor_sha256(authentic_bytes)
    authentic_eval = hashlib.sha256(
        open(os.path.join(REPO, "IMPLEMENTATION", "evaluator.py"), "rb").read()
    ).hexdigest()

    # Root keys R1 (pinned) + R2 (designated successor) and the gate's issuer
    # keypair, all generated live; private halves never persisted. R1's public
    # half is pinned to the target out-of-band (base64); the gate's issuer key
    # is handed to pep ONLY via the env-var production path and vouched to the
    # target through the R2-signed key record.
    r1 = Ed25519PrivateKey.generate()
    r2 = Ed25519PrivateKey.generate()
    gate_priv = Ed25519PrivateKey.generate()
    r1_pub_b64 = base64.b64encode(
        r1.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    ).decode("ascii")

    interaction = {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": manifest_sha256(),
    }

    # Gate signs on the DEFAULT path via the production key path.
    signed_env = _gate_sign_via_production_path(
        interaction, TARGET_URL, gate_priv, GATE_KEY_ID
    )
    forge_env = {k: v for k, v in signed_env.items() if k != "issuer_signature"}

    not_after = now + timedelta(hours=24)

    def root_bytes(entries, serial=1):
        rec = build_root_record(R1_ID, r1, entries, serial, not_after, issued_at=now)
        return json.dumps(rec).encode("utf-8")

    def key_bytes(signer_priv, root_id):
        # The key record vouches the GATE's issuer key (GATE_KEY_ID -> gate pub),
        # signed by the named root.
        entry = make_key_entry(GATE_KEY_ID, gate_priv.public_key(),
                               not_before=now - timedelta(days=1),
                               not_after=now + timedelta(days=365))
        rec = build_key_record(root_id, signer_priv, [entry], 1, not_after, issued_at=now)
        return json.dumps(rec).encode("utf-8")

    def active(rid, pub, successor_of=None):
        return make_root_entry(rid, pub, "active", now - timedelta(days=1),
                               now + timedelta(days=365), successor_of=successor_of)

    # Root records: designation (R1 active, R2 active successor), revoked-R2,
    # retired-R2, and a stale designation (record not_after in the past).
    designation_bytes = root_bytes([active(R1_ID, r1.public_key()),
                                    active(R2_ID, r2.public_key(), successor_of=R1_ID)])
    revoked_bytes = root_bytes([active(R1_ID, r1.public_key()),
                                make_root_entry(R2_ID, r2.public_key(), "revoked",
                                                now - timedelta(days=1),
                                                now + timedelta(days=365),
                                                revoked_at=now - timedelta(minutes=5))],
                               serial=2)
    retired_bytes = root_bytes([active(R1_ID, r1.public_key()),
                                make_root_entry(R2_ID, r2.public_key(), "retired",
                                                now - timedelta(days=1),
                                                now + timedelta(days=365),
                                                retired_at=now - timedelta(hours=1))],
                               serial=3)
    stale_root = build_root_record(R1_ID, r1,
                                   [active(R1_ID, r1.public_key()),
                                    active(R2_ID, r2.public_key(), successor_of=R1_ID)],
                                   1, now - timedelta(hours=1), issued_at=now - timedelta(hours=2))
    stale_bytes = json.dumps(stale_root).encode("utf-8")

    # The key record signed by the designated-active R2 (vouches the gate key).
    r2_key_bytes = key_bytes(r2, R2_ID)

    # Publishers (each on its own real socket).
    pub_url, pub_httpd = _serve(authentic_bytes)
    desig_url, desig_httpd = _serve(designation_bytes)
    revoked_url, revoked_httpd = _serve(revoked_bytes)
    retired_url, retired_httpd = _serve(retired_bytes)
    stale_url, stale_httpd = _serve(stale_bytes)
    key_url, key_httpd = _serve(r2_key_bytes)
    # A root URL pointing at a closed port (fetch failure -> fail-closed).
    dead_httpd = socketserver.TCPServer(("127.0.0.1", 0), http.server.BaseHTTPRequestHandler)
    dead_port = dead_httpd.server_address[1]
    dead_httpd.server_close()  # close immediately so connections refuse
    dead_url = "http://127.0.0.1:%d/record.json" % dead_port

    # TARGET tree: a genuinely mutated copy (evaluator.py differs from the gate).
    tdir = tempfile.mkdtemp(prefix="root_recovery_target_")
    for sub in ("IMPLEMENTATION", "CANON", "MANIFEST", "EVIDENCE"):
        shutil.copytree(os.path.join(REPO, sub), os.path.join(tdir, sub))
    eval_path = os.path.join(tdir, "IMPLEMENTATION", "evaluator.py")
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write("\n# VL-049 root-recovery demo: divergent target tree\n")
    target_eval = hashlib.sha256(open(eval_path, "rb").read()).hexdigest()
    open(os.path.join(tdir, "target_driver.py"), "w", encoding="utf-8").write(TARGET_DRIVER)
    assert target_eval != authentic_eval, "target tree must genuinely differ"

    def run_target(envelope, root_url, key_url_arg, publisher_url=pub_url):
        payload = {
            "envelope": envelope, "interaction": interaction,
            "target_url": TARGET_URL, "publisher_url": publisher_url,
            "pinned_root_sha": pinned_root_sha,
            "root_url": root_url, "key_url": key_url_arg,
            "r1_pub_b64": r1_pub_b64, "r1_id": R1_ID,
            "now": now.isoformat(),
        }
        fpath = os.path.join(tdir, "case.json")
        json.dump(payload, open(fpath, "w"))
        env = dict(os.environ, PYTHONPATH=tdir)
        # The target must NOT inherit the gate's signing key env.
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
    print("ROOT-RECOVERY cross-host rotation demonstration (VL-049)")
    print("=" * 74)
    print("Pinned published-record anchor : %s" % pinned_root_sha)
    print("Gate evaluator sha256          : %s" % authentic_eval)
    print("TARGET local evaluator         : %s  <- genuinely divergent" % target_eval)
    print("Gate issuer key_id             : %s  (via ELYON_SIGNING_KEY_* env)" % GATE_KEY_ID)
    print("Target pins ONLY               : %s (out-of-band; never re-pinned)" % R1_ID)
    print("-" * 74)

    cases = [
        ("KILLER: signed valid; R1 designates R2; key vouched by R2 (DIVERGENT disk)",
         signed_env, desig_url, key_url, True, "REASSERTED_AND_BOUND"),
        ("keyless forge (no signature); R2-vouched key",
         forge_env, desig_url, key_url, False, "REF_VERIFY_SIGNATURE_INVALID"),
        ("revoked R2 signs the key record",
         signed_env, revoked_url, key_url, False, "REF_VERIFY_ROOT_REVOKED"),
        ("retired R2 signs a NEW key record",
         signed_env, retired_url, key_url, False, "REF_VERIFY_ROOT_RETIRED"),
        ("root-record fetch failure (dead socket)",
         signed_env, dead_url, key_url, False, "REF_VERIFY_ROOT_RECORD_INVALID"),
        ("stale root record (now >= not_after)",
         signed_env, stale_url, key_url, False, "REF_VERIFY_ROOT_RECORD_STALE"),
    ]

    ok = True
    results = []
    for label, env, r_url, k_url, exp_honored, exp_reason in cases:
        v = run_target(env, r_url, k_url)
        passed = (v["honored"] == exp_honored and v["reason"] == exp_reason)
        ok = ok and passed
        results.append((label, v, passed))
        print("[%s] %s" % ("PASS" if passed else "FAIL", label))
        print("       honored=%s reason=%s" % (v["honored"], v["reason"]))
        if v.get("local_disk_contrast_reason") not in (None, "n/a"):
            print("       (local-disk verify on this divergent tree would have"
                  " returned: %s)" % v["local_disk_contrast_reason"])

    print("-" * 74)
    # KILLER PROPERTY: the valid case was HONORED despite the divergent disk via
    # the R2-vouched key + the fetched currency record, AND the local-disk
    # contrast shows currency would have refused on this divergent tree.
    valid_v = results[0][1]
    killer = (valid_v["honored"] is True
              and valid_v["local_disk_contrast_reason"]
              == "REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED")
    print("KILLER PROPERTY (R2-vouched honor despite divergent disk + local-disk-would-refuse): %s"
          % ("HOLDS" if killer else "FAILED"))
    ok = ok and killer

    for h in (pub_httpd, desig_httpd, revoked_httpd, retired_httpd, stale_httpd, key_httpd):
        h.shutdown()
    shutil.rmtree(tdir, ignore_errors=True)
    os.environ.pop("ELYON_SIGNING_KEY_HEX", None)
    os.environ.pop("ELYON_SIGNING_KEY_ID", None)

    print("=" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    print("Scope: planned in-band R1->R2 rotation over real transport, no shortcut.")
    print("Does NOT close root-key COMPROMISE recovery (out-of-band; artifact 11 s2).")
    print("Does NOT assert true multi-machine / TLS (G5 floor).")
    print("'forgery-resistant' stays bounded and out of any deposit.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
