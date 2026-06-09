"""
Real MCP server proof (docs/restructure/17_mcp_server_spec.md, increment VL-077, B4).

Closes the wedge demo's stated fidelity gap. Whereas wedge_agent_toolcall_001_runner.py drives
the executor gate IN-PROCESS (TestClient, no MCP protocol), this runner spawns
IMPLEMENTATION/mcp_server.py as a REAL SUBPROCESS and speaks JSON-RPC 2.0 over its real stdin/
stdout pipes (the MCP stdio transport): the `initialize` handshake, the `notifications/
initialized` notification, then `tools/call` over the wire.

It proves the wedge property holds on a genuine MCP `tools/call` surface: the side-effecting tool
fires exactly once (the admitted call), and is refused - unfired - when the call is un-attested,
replayed, rebound (different tool / args), drifted (a re-published evaluator state), or stale
(past its decision-freshness window). The admitted/adversarial envelopes are produced by the REAL
gate (pep). Exactly-once is confirmed across the process boundary by the server's read-only
elyon-sol/executed_count method (count == 1).

Honest scope: stdio is a real transport and a real process boundary, but LOCAL. Cross-host TLS is
proven separately (g5_multiprocess_tls_001_runner.py / Phase C). This runner certifies the MCP
protocol + transport fidelity and the refusal matrix, not a real external attacker on a network.

Run:  PYTHONPATH=. python3 EVIDENCE/proofs/mcp_server_001_runner.py
Exits 0 iff every case matches and the tool fired exactly once.
"""

import json
import os
import subprocess
import sys
import tempfile
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.mcp_server import interaction_for, ENVELOPE_META_KEY
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_BINDING_MISMATCH,
    REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_REPLAY,
)

TARGET_ID = "mcp://elyon-sol/tool-server"
GATE_KID = "gate-mcp-proof-001"
AUTHENTIC = "EVIDENCE/published_hashes.json"

_priv = Ed25519PrivateKey.generate()
_pub_hex = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def admit(tool, args, max_age=300):
    """Drive the REAL gate (pep) to admit a tool call; return the signed envelope."""
    class _R:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        return _R()

    pep._INJECTED_SIGNING_KEY = (_priv, GATE_KID)
    pep.DECISION_MAX_AGE_SECONDS = max_age
    orig = pep.requests.post
    pep.requests.post = fake_post
    try:
        r = TestClient(pep.app).post(
            "/governed-call",
            json={"target_url": TARGET_ID, "interaction": interaction_for(tool, args)},
        )
        assert r.status_code == 200, r.text
        return r.json()["envelope"]
    finally:
        pep.requests.post = orig
        pep.DECISION_MAX_AGE_SECONDS = 300


class Server:
    """A real MCP server subprocess, spoken to over stdio."""

    def __init__(self, record_path):
        env = dict(os.environ)
        env["PYTHONPATH"] = "."
        env["ELYON_MCP_GATE_KEY_ID"] = GATE_KID
        env["ELYON_MCP_GATE_PUBLIC_KEY_HEX"] = _pub_hex
        env["ELYON_MCP_TARGET_ID"] = TARGET_ID
        env["ELYON_MCP_RECORD_PATH"] = record_path
        self.p = subprocess.Popen(
            [sys.executable, "-m", "IMPLEMENTATION.mcp_server"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, text=True, bufsize=1,
        )
        self._id = 0

    def _send(self, msg):
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def _rpc(self, method, params=None):
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        line = self.p.stdout.readline()
        return json.loads(line)

    def handshake(self):
        resp = self._rpc("initialize", {"protocolVersion": "2025-06-18"})
        assert resp["result"]["serverInfo"]["name"] == "elyon-sol-gated-tools", resp
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return resp["result"]["protocolVersion"]

    def call(self, tool, args, envelope):
        params = {"name": tool, "arguments": args}
        if envelope is not None:
            params["_meta"] = {ENVELOPE_META_KEY: envelope}
        resp = self._rpc("tools/call", params)
        meta = resp["result"]["_meta"]
        return meta["elyon-sol/executed"], meta["elyon-sol/reason"]

    def executed_count(self):
        return self._rpc("elyon-sol/executed_count")["result"]["count"]

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()


def main():
    results = []

    def check(label, got, exp):
        ok = got == exp
        results.append(ok)
        print("[%s] %s\n       got=%s expected=%s" % ("PASS" if ok else "FAIL", label, got, exp))

    print("=" * 74)
    print("REAL MCP SERVER PROOF: tools/call over stdio - VL-077 (B4)")
    print("=" * 74)

    with tempfile.TemporaryDirectory() as td:
        authentic_path = os.path.join(td, "authentic.json")
        authentic_bytes = open(AUTHENTIC, "rb").read()
        with open(authentic_path, "wb") as f:
            f.write(authentic_bytes)

        srv = Server(authentic_path)
        try:
            pv = srv.handshake()
            check("initialize handshake (protocolVersion echoed)", pv, "2025-06-18")

            env = admit("transfer_funds", {"amount": 100, "to": "acct-42"})
            check("admitted call executes the tool",
                  srv.call("transfer_funds", {"amount": 100, "to": "acct-42"}, env),
                  (True, "REASSERTED_AND_BOUND"))
            check("replay of the admitted call refused (exactly-once)",
                  srv.call("transfer_funds", {"amount": 100, "to": "acct-42"}, env),
                  (False, REF_VERIFY_REPLAY))
            check("un-attested call refused (A1)",
                  srv.call("transfer_funds", {"amount": 100, "to": "acct-42"}, None),
                  (False, REF_VERIFY_ENVELOPE_ABSENT))
            check("rebind to a different tool refused",
                  srv.call("delete_database", {"db": "prod"}, env),
                  (False, REF_VERIFY_BINDING_MISMATCH))
            check("rebind to different args refused",
                  srv.call("transfer_funds", {"amount": 999999, "to": "acct-42"}, env),
                  (False, REF_VERIFY_BINDING_MISMATCH))

            count = srv.executed_count()
            check("tool fired EXACTLY ONCE (observed over stdio)", count, 1)
        finally:
            srv.close()

        # Drift: a fresh server process sees a RE-PUBLISHED evaluator state (the
        # evaluator hash moved), anchored on its own bytes. The authentic-state
        # envelope is now invalid.
        drifted_path = os.path.join(td, "drifted.json")
        drifted_bytes = json.dumps(
            {**json.loads(authentic_bytes), "evaluator_sha256": "0" * 64}, sort_keys=True
        ).encode("utf-8")
        with open(drifted_path, "wb") as f:
            f.write(drifted_bytes)
        srv2 = Server(drifted_path)
        try:
            srv2.handshake()
            check("drifted state invalidates the admission",
                  srv2.call("transfer_funds", {"amount": 100, "to": "acct-42"}, env),
                  (False, REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED))
            check("drifted server fired nothing", srv2.executed_count(), 0)
        finally:
            srv2.close()

        # Stale: a short-window admission, presented after it expires, to a fresh
        # server process.
        short_env = admit("transfer_funds", {"amount": 100, "to": "acct-42"}, max_age=1)
        srv3 = Server(authentic_path)
        try:
            srv3.handshake()
            time.sleep(2)
            check("stale admission refused (past freshness window)",
                  srv3.call("transfer_funds", {"amount": 100, "to": "acct-42"}, short_env),
                  (False, REF_VERIFY_SIGNATURE_EXPIRED))
            check("stale server fired nothing", srv3.executed_count(), 0)
        finally:
            srv3.close()

    print("-" * 74)
    ok = all(results)
    print("=" * 74)
    print("RESULT:", "WEDGE PROPERTY HOLDS on a real MCP stdio server" if ok else "VIOLATION")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
