"""
G5 transport-seam proof runner (docs/restructure/12_g5_transport_design.md
step 1).

Proves IMPLEMENTATION/transport.py's seam over REAL TLS between distinct OS
processes (the server is a subprocess; this runner is the client process), with
NO monkeypatching of the transport - contrast the VL-048 cross-host runner,
which fakes the gate-to-target hop (fake_post) and serves records over plain
loopback http.server. Here both hops run through transport.post_to_target /
transport.get_published over a verified TLS socket.

Invariants asserted (each a pass/fail referent, canon section 9 fail-closed):

  1. BYTE-IDENTICAL DEFAULT. With no TLS arguments and no environment override,
     _resolve_verify() == True and _resolve_cert() == None - so the seam's
     default request equals the current direct requests.post / requests.get
     calls. This is the property a later wiring step relies on to change pep.py /
     published_source.py without changing default behavior.
  2. PUSH over verified TLS. post_to_target(verify=<CA>) to the TLS target
     returns 200 and the server confirms it received the X-Elyon-Sol-Envelope
     header and the body intact - the gate-to-target hop works cross-process
     over TLS.
  3. FETCH over verified TLS. get_published(verify=<CA>) returns the published
     record bytes intact - the record-fetch hop works cross-process over TLS.
  4. FAIL-CLOSED push. post_to_target with default verify (True) against the
     untrusted self-signed peer raises SSLError - an unverifiable target is
     refused, not silently honored.
  5. FAIL-CLOSED fetch. get_published with default verify (True) against the
     untrusted self-signed peer raises SSLError - an unverifiable publisher is
     refused.

Honest bound: this proves the in-env transport SUBSTRATE (real TLS, real cert
verification, distinct OS processes on ONE host). It does NOT prove the full
gate->target->publisher chain (that is steps 2-4), it does NOT use docker
(unavailable in-env), it is NOT true multi-machine, and the attacker is the
author - so it is finish line (A) substrate, not G5 closed (B). The seam has no
callers yet (build-then-wire); pep.py and published_source.py are unchanged.

Run from repo root:
  PYTHONPATH=. python3 EVIDENCE/proofs/g5_transport_seam_001_runner.py
Exits 0 iff all invariants hold; nonzero otherwise.

Artifact: docs/restructure/12_g5_transport_design.md step 1.
"""

import os
import subprocess
import sys
import tempfile
import textwrap
import time

import requests

from IMPLEMENTATION.transport import (
    _resolve_verify,
    _resolve_cert,
    post_to_target,
    get_published,
)

HOST = "127.0.0.1"
PORT = 8443
TARGET_URL = "https://%s:%d/target" % (HOST, PORT)
PUBLISH_URL = "https://%s:%d/published_hashes.json" % (HOST, PORT)
RECORD_BYTES = b'{"canon_sha256":"aa","evaluator_sha256":"bb","manifest_sha256":"cc"}'
ENVELOPE_HEADER = "signed-envelope-stub-for-seam-proof"

# A standing TLS server (subprocess) that answers both hops: GET returns the
# published record bytes; POST echoes whether it saw the attestation header and
# the body length. It is a real separate OS process bound to a real TLS socket.
SERVER_SRC = textwrap.dedent(
    '''
    import http.server, ssl, sys, os, json
    RECORD = %(record)r
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(RECORD)))
            self.end_headers()
            self.wfile.write(RECORD)
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n)
            payload = json.dumps({
                "saw_header": self.headers.get("X-Elyon-Sol-Envelope", ""),
                "body_len": len(body),
            }).encode("ascii")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        def log_message(self, *a):
            pass
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(sys.argv[1], sys.argv[2])
    httpd = http.server.HTTPServer((%(host)r, %(port)d), H)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    print("SERVER_UP", flush=True)
    httpd.serve_forever()
    '''
) % {"record": RECORD_BYTES, "host": HOST, "port": PORT}


def _gen_cert(tmpdir):
    """Generate a self-signed cert/key for 127.0.0.1 via the openssl CLI."""
    cert = os.path.join(tmpdir, "cert.pem")
    key = os.path.join(tmpdir, "key.pem")
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", key, "-out", cert, "-days", "1",
            "-subj", "/CN=127.0.0.1",
            "-addext", "subjectAltName=IP:127.0.0.1",
        ],
        check=True, capture_output=True,
    )
    return cert, key


def main():
    results = []

    def check(label, passed, detail=""):
        results.append((label, passed, detail))
        print("[%s] %s%s" % ("PASS" if passed else "FAIL", label,
                              ("  (%s)" % detail) if detail else ""))

    # ----- Invariant 1: byte-identical default resolution -----
    # No env override expected; make sure the test environment is clean.
    os.environ.pop("ELYON_TLS_CA_BUNDLE", None)
    os.environ.pop("ELYON_TLS_CLIENT_CERT", None)
    v = _resolve_verify(None)
    c = _resolve_cert(None)
    check("byte-identical default: verify resolves to True", v is True, "got %r" % (v,))
    check("byte-identical default: client cert resolves to None", c is None, "got %r" % (c,))

    tmpdir = tempfile.mkdtemp(prefix="g5_seam_")
    cert, key = _gen_cert(tmpdir)

    server = subprocess.Popen(
        [sys.executable, "-c", SERVER_SRC, cert, key],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        # Wait for SERVER_UP (bounded).
        up = False
        for _ in range(50):
            line = server.stdout.readline()
            if line.strip() == "SERVER_UP":
                up = True
                break
            if server.poll() is not None:
                break
        check("TLS server (separate OS process) came up", up,
              "pid=%s" % server.pid)
        time.sleep(0.2)

        # ----- Invariant 2: push over verified TLS -----
        try:
            r = post_to_target(
                TARGET_URL,
                {"interaction": "x"},
                {"X-Elyon-Sol-Envelope": ENVELOPE_HEADER},
                verify=cert,
            )
            body = r.json()
            passed = (r.status_code == 200
                      and body.get("saw_header") == ENVELOPE_HEADER
                      and body.get("body_len", 0) > 0)
            check("push over verified TLS (header+body intact)", passed,
                  "status=%s saw_header=%r" % (r.status_code, body.get("saw_header")))
        except Exception as e:
            check("push over verified TLS (header+body intact)", False,
                  "%s: %s" % (type(e).__name__, e))

        # ----- Invariant 3: fetch over verified TLS -----
        try:
            r = get_published(PUBLISH_URL, verify=cert)
            passed = (r.status_code == 200 and r.content == RECORD_BYTES)
            check("fetch over verified TLS (record bytes intact)", passed,
                  "status=%s len=%d" % (r.status_code, len(r.content)))
        except Exception as e:
            check("fetch over verified TLS (record bytes intact)", False,
                  "%s: %s" % (type(e).__name__, e))

        # ----- Invariant 4: fail-closed push (default verify, untrusted cert) ---
        try:
            post_to_target(
                TARGET_URL,
                {"interaction": "x"},
                {"X-Elyon-Sol-Envelope": ENVELOPE_HEADER},
            )
            check("fail-closed push (untrusted self-signed)", False,
                  "UNEXPECTEDLY SUCCEEDED")
        except requests.exceptions.SSLError:
            check("fail-closed push (untrusted self-signed)", True,
                  "SSLError as required")
        except Exception as e:
            check("fail-closed push (untrusted self-signed)", False,
                  "wrong error: %s" % type(e).__name__)

        # ----- Invariant 5: fail-closed fetch (default verify, untrusted cert) --
        try:
            get_published(PUBLISH_URL)
            check("fail-closed fetch (untrusted self-signed)", False,
                  "UNEXPECTEDLY SUCCEEDED")
        except requests.exceptions.SSLError:
            check("fail-closed fetch (untrusted self-signed)", True,
                  "SSLError as required")
        except Exception as e:
            check("fail-closed fetch (untrusted self-signed)", False,
                  "wrong error: %s" % type(e).__name__)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except Exception:
            server.kill()

    ok = all(p for _, p, _ in results)
    print("-" * 74)
    print("RESULT: %s" % ("ALL INVARIANTS HOLD" if ok else "INVARIANT VIOLATION"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
