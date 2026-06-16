"""
ext-authz sidecar over REAL loopback TLS - in-sandbox proof runner (VL-105).

Stronger than the hermetic in-memory handshake (TESTS/deploy/test_authz_sidecar_tls.py):
this stands up the PRODUCTION sidecar (IMPLEMENTATION/authz_sidecar.py) on a real
uvicorn server under TLS (uvicorn --ssl-* with a dev-CA `elyon-authz` leaf), mints a
real signed envelope from the gate (pep), and drives ALLOW + DENY decisions over an
HTTPS client that VERIFIES the server against the dev CA. It proves the sidecar's
decision path works unchanged over real TLS transport, in-process but over a real
socket.

CI-excluded (parity with g5_multiprocess_tls): GitHub hosted runners do not reliably
reach a loopback-TLS uvicorn within the readiness budget - an environment
incompatibility, not a logic bug. The CI-gated equivalent is the in-memory handshake
test above; the real two-host TLS run is the author's (deploy/elyon-authz/VM_TLS_TEST.md).

Run (in the sandbox or locally):
    PYTHONPATH=. python3 EVIDENCE/proofs/authz_sidecar_tls_001_runner.py
Exits 0 iff a valid attested request is ALLOWED (200) over TLS and a tampered one is
DENIED (403); non-zero otherwise.
"""

import os
import sys
import tempfile
import threading
import time
from datetime import timedelta

import httpx
import uvicorn
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

import deploy.tls.gen_certs as g
import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.authz_sidecar import build_authz_sidecar_app
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.published_source import anchor_sha256

TARGET_ID = "mcp://elyon-sol/tool-server"
KEY_ID = "gate-test-ed25519-001"
HOST, PORT = "127.0.0.1", 9247


def _mint_envelope(args):
    """A real signed envelope from the gate (its upstream push is faked - no socket)."""
    class _R:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        return _R()

    orig = pep.requests.post
    pep.requests.post = fake_post
    try:
        r = TestClient(pep.app).post(
            "/governed-call",
            json={"target_url": TARGET_ID, "interaction": interaction_for("transfer_funds", args)},
        )
        assert r.status_code == 200, r.text
        return r.json()["envelope"]
    finally:
        pep.requests.post = orig


def main() -> int:
    tmp = tempfile.mkdtemp()
    # Dev CA + an elyon-authz leaf (SAN covers localhost for the loopback client).
    ca_key, ca_cert = g.gen_ca()
    leaf_key, leaf_cert = g.gen_leaf(ca_key, ca_cert, "elyon-authz", ["elyon-authz", "localhost", "127.0.0.1"])
    ca_p = os.path.join(tmp, "ca.crt")
    crt_p = os.path.join(tmp, "elyon-authz.crt")
    key_p = os.path.join(tmp, "elyon-authz.key")
    open(ca_p, "wb").write(g.cert_pem(ca_cert))
    open(crt_p, "wb").write(g.cert_pem(leaf_cert))
    open(key_p, "wb").write(g.key_pem(leaf_key))

    # A gate signing key, installed into pep, also pinned in the sidecar config.
    priv = Ed25519PrivateKey.generate()
    pep._get_signing_key = lambda: (priv, KEY_ID)

    args = {"amount": 100, "to": "acct-42"}
    env = _mint_envelope(args)

    rec = open("EVIDENCE/published_hashes.json", "rb").read()
    config = {
        "target_url": TARGET_ID,
        "record_bytes": rec,
        "pinned_root_sha256": anchor_sha256(rec),
        "pinned_public_keys": {KEY_ID: priv.public_key()},
        "clock_skew": timedelta(0),
    }
    app = build_authz_sidecar_app(config_provider=lambda: config)

    server = uvicorn.Server(
        uvicorn.Config(app, host=HOST, port=PORT, ssl_certfile=crt_p, ssl_keyfile=key_p, log_level="error")
    )
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    try:
        for _ in range(100):
            if server.started:
                break
            time.sleep(0.1)
        else:
            print("FAIL: TLS server did not start")
            return 1

        # trust_env=False so a SOCKS/HTTP proxy in the environment is ignored on loopback.
        client = httpx.Client(verify=ca_p, trust_env=False, timeout=5.0)
        interaction = interaction_for("transfer_funds", args)
        base = f"https://localhost:{PORT}/authz"

        # ALLOW: a valid attested request over verified TLS.
        allow = client.post(base, headers={
            "X-Elyon-Sol-Envelope": canonical_json(env),
            "X-Elyon-Sol-Interaction": canonical_json(interaction),
        })
        # DENY: tamper a signed-region field -> signature invalid.
        bad = dict(env)
        bad["request_context"] = dict(bad["request_context"])
        bad["request_context"]["AP"] = list(bad["request_context"]["AP"]) + ["smuggled"]
        deny = client.post(base, headers={
            "X-Elyon-Sol-Envelope": canonical_json(bad),
            "X-Elyon-Sol-Interaction": canonical_json(interaction),
        })

        ok = True
        if not (allow.status_code == 200 and allow.headers.get("x-elyon-decision") == "ALLOW"):
            print(f"FAIL ALLOW: {allow.status_code} {allow.headers.get('x-elyon-decision')} {allow.headers.get('x-elyon-reason')}")
            ok = False
        else:
            print(f"PASS ALLOW over TLS: 200 ALLOW ({allow.headers.get('x-elyon-reason')})")
        if not (deny.status_code == 403 and deny.headers.get("x-elyon-decision") == "DENY"):
            print(f"FAIL DENY: {deny.status_code} {deny.headers.get('x-elyon-decision')} {deny.headers.get('x-elyon-reason')}")
            ok = False
        else:
            print(f"PASS DENY over TLS: 403 DENY ({deny.headers.get('x-elyon-reason')})")
        print("RESULT:", "OK" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        server.should_exit = True
        t.join(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
