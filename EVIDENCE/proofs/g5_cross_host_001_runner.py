"""
G5 cross-host transport evidence runner (VL-039, T-G5-transport).

Stands up a real two-context demonstration over loopback:

  - PUBLISHER: a stdlib HTTP server (127.0.0.1, ephemeral port) serving the
    AUTHENTIC EVIDENCE/published_hashes.json bytes. A second server serves a
    TAMPERED record (different bytes) for the anchor-failure case.
  - TARGET: a SUBPROCESS whose working tree is a copy of the repo with
    IMPLEMENTATION/evaluator.py BYTE-MUTATED, so its local evaluator hash
    genuinely differs from the gate's (constraint (k): a target whose local
    disk is genuinely mutated to differ, reached over real loopback). The
    target fetches the published record from the publisher, anchor-verifies
    it against the pinned root (Decision B-prime-1), and runs
    verify_envelope(..., record_source=<fetched record>) so currency comes
    from the FETCHED record, not its own (mutated) disk (Decision C / D-b).

The load-bearing result: the target HONORS a valid envelope built against the
authentic evaluator DESPITE its own divergent local disk (because it trusts
the fetched record), and the reported local-disk contrast shows a VL-038-style
local-disk verify would have REFUSED the same valid envelope
(RE-EVALUATE-REQUIRED). It still REFUSES a forged envelope and a fetched
record that fails the pinned anchor.

Run from repo root:  PYTHONPATH=. python3 EVIDENCE/proofs/g5_cross_host_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.
"""

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

from IMPLEMENTATION.envelope import build_envelope, canonical_json
from IMPLEMENTATION.evaluator import load_manifest, manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256

REPO = os.getcwd()
TARGET_URL = "http://127.0.0.1:9000/target"
PUBLISHED_PATH = os.path.join(REPO, "EVIDENCE", "published_hashes.json")


def _serve(record_bytes):
    """Start a loopback HTTP server serving record_bytes; return (base_url, httpd)."""
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


TARGET_DRIVER = '''\
import json, sys
from IMPLEMENTATION.published_source import fetch_published_record
from IMPLEMENTATION.verifier import verify_envelope
from IMPLEMENTATION.envelope import _evaluator_sha256

inp = json.load(open(sys.argv[1]))
record = fetch_published_record(inp["publisher_url"], inp["pinned_root"])
out = {"local_evaluator_sha256": _evaluator_sha256()}
if record is None:
    out.update(honored=False, reason="REF_TARGET_ANCHOR_MISMATCH",
               local_disk_contrast_reason="n/a")
    print(json.dumps(out)); sys.exit(0)
env = inp["envelope"]
res = verify_envelope(env, inp["interaction"], inp["target_url"], record_source=record)
contrast = (verify_envelope(env, inp["interaction"], inp["target_url"])["reason"]
            if env is not None else "n/a")
out.update(honored=res["accepted"], reason=res["reason"],
           local_disk_contrast_reason=contrast)
print(json.dumps(out))
'''


def main():
    authentic_bytes = open(PUBLISHED_PATH, "rb").read()
    pinned_root = anchor_sha256(authentic_bytes)
    authentic_eval = hashlib.sha256(
        open(os.path.join(REPO, "IMPLEMENTATION", "evaluator.py"), "rb").read()
    ).hexdigest()

    # Envelopes built in the AUTHENTIC process (the gate's view).
    interaction = {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": manifest_sha256(),
    }
    valid_env = build_envelope(
        decision="ELIGIBLE", target_url=TARGET_URL,
        normalized_interaction=interaction, manifest=load_manifest(),
        ac3=True, t26=True, manifest_integrity=True,
        timestamp_utc="2026-05-31T00:00:00+00:00",
    )
    forged_env = json.loads(canonical_json(valid_env))
    forged_env["request_context"]["AP"] = ["identity", "role", "admin"]  # tamper, no rehash

    # Publishers: authentic and tampered (different bytes -> fails pinned anchor).
    auth_url, auth_httpd = _serve(authentic_bytes)
    tampered_bytes = authentic_bytes.replace(b"0.9.8.4", b"6.6.6.6")
    tamp_url, tamp_httpd = _serve(tampered_bytes)

    # TARGET tree: a genuinely mutated copy (evaluator.py differs from the gate).
    tdir = tempfile.mkdtemp(prefix="g5_target_")
    for sub in ("IMPLEMENTATION", "CANON", "MANIFEST", "EVIDENCE"):
        shutil.copytree(os.path.join(REPO, sub), os.path.join(tdir, sub))
    eval_path = os.path.join(tdir, "IMPLEMENTATION", "evaluator.py")
    with open(eval_path, "a", encoding="utf-8") as f:
        f.write("\n# G5 demo: deliberately divergent target tree (VL-039)\n")
    target_eval = hashlib.sha256(open(eval_path, "rb").read()).hexdigest()
    open(os.path.join(tdir, "target_driver.py"), "w", encoding="utf-8").write(TARGET_DRIVER)

    assert target_eval != authentic_eval, "target tree must genuinely differ"

    def run_target(envelope, publisher_url):
        payload = {
            "envelope": envelope, "interaction": interaction,
            "target_url": TARGET_URL, "publisher_url": publisher_url,
            "pinned_root": pinned_root,
        }
        fpath = os.path.join(tdir, "case.json")
        json.dump(payload, open(fpath, "w"))
        env = dict(os.environ, PYTHONPATH=tdir)
        r = subprocess.run([sys.executable, os.path.join(tdir, "target_driver.py"), fpath],
                           cwd=tdir, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("target subprocess failed: " + r.stderr)
        return json.loads(r.stdout.strip())

    print("=" * 74)
    print("G5 cross-host transport demonstration (VL-039)")
    print("=" * 74)
    print("Pinned anchor (sha256 of EVIDENCE/published_hashes.json): %s" % pinned_root)
    print("Gate evaluator sha256   : %s" % authentic_eval)
    print("TARGET local evaluator  : %s  <- genuinely divergent" % target_eval)
    print("Publisher (authentic)   : %s" % auth_url)
    print("Publisher (tampered)    : %s" % tamp_url)
    print("-" * 74)

    cases = [
        ("valid envelope, authentic record (DIVERGENT target disk)", valid_env, auth_url,
         True, "REASSERTED_AND_BOUND"),
        ("forged envelope, authentic record", forged_env, auth_url,
         False, "REF_VERIFY_REASSERT_INVALIDATED"),
        ("valid envelope, tampered record (fails pinned anchor)", valid_env, tamp_url,
         False, "REF_TARGET_ANCHOR_MISMATCH"),
        ("no envelope (A1), authentic record", None, auth_url,
         False, "REF_VERIFY_ENVELOPE_ABSENT"),
    ]

    ok = True
    results = []
    for label, env, purl, exp_honored, exp_reason in cases:
        v = run_target(env, purl)
        passed = (v["honored"] == exp_honored and v["reason"] == exp_reason)
        ok = ok and passed
        results.append((label, v, exp_honored, exp_reason, passed))
        print("[%s] %s" % ("PASS" if passed else "FAIL", label))
        print("       honored=%s reason=%s" % (v["honored"], v["reason"]))
        if v.get("local_disk_contrast_reason") not in (None, "n/a"):
            print("       (VL-038 local-disk verify on this divergent tree would have"
                  " returned: %s)" % v["local_disk_contrast_reason"])

    print("-" * 74)
    # Load-bearing invariant: the valid case was HONORED despite the divergent
    # disk, AND the local-disk contrast shows it would have been refused.
    valid_v = results[0][1]
    killer = (valid_v["honored"] is True
              and valid_v["local_disk_contrast_reason"] == "REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED")
    print("KILLER PROPERTY (honor-valid-despite-divergent-disk + local-disk-would-refuse): %s"
          % ("HOLDS" if killer else "FAILED"))
    ok = ok and killer

    auth_httpd.shutdown(); tamp_httpd.shutdown()
    shutil.rmtree(tdir, ignore_errors=True)

    print("=" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
