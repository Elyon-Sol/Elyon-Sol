"""
Enforcement census, LOCAL-RECEIVER variant (hermetic). Repo path:
EVIDENCE/proofs/enforcement_census_local_001_runner.py.

The Revision 8 enforcement-evidence addendum (Zenodo 10.5281/zenodo.21364720)
reports a 204-call census - 102 REFUSE -> 403 with zero external side effects,
102 ELIGIBLE -> 200 with exactly one external POST each - measured by a loopback
receiver in a separate process from the gate, but names no committed harness for
that variant (only the third-party webhook runner,
external_interception_webhook_001_runner.py, which is NON-hermetic). This runner
IS that harness, committed, so the census is reproducible by anyone from the
repository with no external account:

  - the gate (IMPLEMENTATION.pep) is started as a SUBPROCESS with an ephemeral
    Ed25519 signing key, exactly as the webhook runner does;
  - the receiver is an HTTP server in THIS process, on a loopback port, counting
    every POST it receives and the X-Elyon-Sol-Envelope header on each;
  - the call pattern is the webhook runner's, verbatim: 1 REFUSE + 1 ELIGIBLE
    sanity pair, 50 REFUSE then 50 ELIGIBLE, then 51 alternating pairs
    = 204 calls, 102 REFUSE, 102 ELIGIBLE.

Because the receiver is on loopback, the gate's SSRF guard would refuse the
forward; the gate is started with the documented dev/test opt-out
ELYON_ALLOW_PRIVATE_TARGETS=1 (its blocking is covered by test_ssrf_guard.py).
The measured property - zero forwards on REFUSE, exactly one per ELIGIBLE, every
forward carrying a signed envelope with a distinct decision_id - is unaffected
by where the receiver sits.

Exit 0 iff every expectation holds; non-zero otherwise. Hermetic: loopback only,
no network, no fixed ports (both ports are allocated free), so CI runs it.
"""

import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = os.getcwd()
sys.path.insert(0, REPO)
from IMPLEMENTATION.evaluator import manifest_sha256  # noqa: E402

MANIFEST_SHA = manifest_sha256()


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# --- the receiver: a separate HTTP server in this process, counting side effects ---
received = {"posts": 0, "with_envelope": 0, "decision_ids": [], "other_methods": 0}
_lock = threading.Lock()


class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        self.rfile.read(n)
        env_hdr = self.headers.get("X-Elyon-Sol-Envelope")
        with _lock:
            received["posts"] += 1
            if env_hdr:
                received["with_envelope"] += 1
                try:
                    received["decision_ids"].append(json.loads(env_hdr).get("decision_id"))
                except ValueError:
                    received["decision_ids"].append(None)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        with _lock:
            received["other_methods"] += 1
        self.send_response(405)
        self.end_headers()

    def log_message(self, *a):
        pass


def start_gate(port):
    priv = Ed25519PrivateKey.generate()
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO
    env["ELYON_SIGNING_KEY_HEX"] = priv.private_bytes_raw().hex()
    env["ELYON_SIGNING_KEY_ID"] = "census-local-001"
    env["ELYON_ALLOW_PRIVATE_TARGETS"] = "1"  # loopback receiver; see module docstring
    env.pop("ELYON_TARGET_URL_ALLOWLIST", None)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "IMPLEMENTATION.pep:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


results = {"refuse_calls": 0, "refuse_403": 0, "eligible_calls": 0,
           "eligible_200": 0, "unexpected": 0}


def body(eligible, target_url):
    """REFUSE: empty AP/OP (schema-valid, evaluator REFUSE). ELIGIBLE: the manifest's
    required sets. Same shapes as the webhook runner."""
    return {
        "target_url": target_url,
        "interaction": {
            "AP": (["identity", "role"] if eligible else []),
            "OP": (["session", "request"] if eligible else []),
            "context": {},
            "expected_manifest_version": "1.0",
            "expected_manifest_sha256": MANIFEST_SHA,
        },
    }


def main():
    recv_port = _free_port()
    server = ThreadingHTTPServer(("127.0.0.1", recv_port), Receiver)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    target_url = "http://127.0.0.1:%d/receiver" % recv_port

    gate_port = _free_port()
    gate_url = "http://127.0.0.1:%d/governed-call" % gate_port
    gate = start_gate(gate_port)
    try:
        ready = False
        for _ in range(80):
            try:
                r = requests.post(gate_url, json=body(False, target_url), timeout=3)
                if r.status_code in (200, 403):
                    ready = True
                    break
            except requests.RequestException:
                time.sleep(0.25)
        if not ready:
            print("FAIL: gate did not become ready")
            return 1
        # readiness probe was a REFUSE: reset the tallies so the census is exactly 204
        for k in results:
            results[k] = 0
        with _lock:
            received.update({"posts": 0, "with_envelope": 0, "decision_ids": [], "other_methods": 0})

        def call(eligible):
            r = requests.post(gate_url, json=body(eligible, target_url), timeout=15)
            if eligible:
                results["eligible_calls"] += 1
                results["eligible_200" if r.status_code == 200 else "unexpected"] += 1
            else:
                results["refuse_calls"] += 1
                results["refuse_403" if r.status_code == 403 else "unexpected"] += 1

        call(False); call(True)                      # sanity pair
        for _ in range(50): call(False)              # block 2
        for _ in range(50): call(True)
        for _ in range(51): call(False); call(True)  # block 3, alternating
        time.sleep(0.5)
    finally:
        gate.terminate()
        try:
            gate.wait(timeout=10)
        except subprocess.TimeoutExpired:
            gate.kill()
        server.shutdown()

    total = results["refuse_calls"] + results["eligible_calls"]
    with _lock:
        posts = received["posts"]
        with_env = received["with_envelope"]
        ids = received["decision_ids"]
    distinct = len(set(i for i in ids if i))
    rows = [
        ("Manifest SHA-256", MANIFEST_SHA[:8]),
        ("Total HTTP calls", total),
        ("REFUSE calls (expected 403)", results["refuse_calls"]),
        ("REFUSE returning 403", results["refuse_403"]),
        ("ELIGIBLE calls (expected 200)", results["eligible_calls"]),
        ("ELIGIBLE returning 200", results["eligible_200"]),
        ("Unexpected HTTP outcomes", results["unexpected"]),
        ("External POSTs observed (loopback receiver)", posts),
        ("External POSTs carrying a signed envelope", with_env),
        ("Distinct decision_id values among them", distinct),
        ("External POSTs from REFUSE calls", posts - results["eligible_200"] if posts >= results["eligible_200"] else "n/a"),
        ("Duplicate external executions", len(ids) - distinct),
    ]
    print("=" * 72)
    print("ENFORCEMENT CENSUS - local loopback receiver (separate process from the gate)")
    print("=" * 72)
    for k, v in rows:
        print("  %-46s %s" % (k, v))
    ok = (total == 204 and results["refuse_calls"] == 102 and results["refuse_403"] == 102
          and results["eligible_calls"] == 102 and results["eligible_200"] == 102
          and results["unexpected"] == 0 and posts == 102 and with_env == 102
          and distinct == 102)
    print("-" * 72)
    print("RESULT: %s" % ("ALL EXPECTED" if ok else "UNEXPECTED OUTCOME(S)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
