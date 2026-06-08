"""
Wedge demonstration: agent tool-call admissibility (MCP-shaped). VL-066 (candidate).

Proves the wedge property on an agent tool-calling surface: a side-effecting TOOL executes
ONLY when the call carries a valid Elyon-Sol admissibility envelope BOUND to that exact tool
call, whose justifying state is CURRENT and whose admission is FRESH. The tool is refused -
and does NOT fire - when the call is:
  - un-attested (no envelope; the agent bypassed the gate),
  - rebound (an envelope admitted for tool A presented for tool B / different args),
  - replayed (the SAME admitted call re-presented within its freshness window),
  - drifted (the policy/evaluator state that justified it has changed), or
  - stale (presented past its decision-freshness window).

The observable is an executed-actions list on the tool server: it must contain exactly the
one admitted call and nothing else.

FIDELITY (honest scope): this models the MCP `tools/call` request shape and the EXECUTOR-side
admissibility gate. It does NOT implement the full MCP protocol (no initialize handshake,
capability negotiation, or stdio transport). Real cross-host TLS transport is proven
separately by EVIDENCE/proofs/g5_multiprocess_tls_001_runner.py; this runner is in-process
(TestClient) and uses an in-memory published record, to isolate the agent/tool SEMANTICS and
the drift/staleness invalidation. It reuses the production verifier, envelope, and gate as-is.

Run:  PYTHONPATH=. python3 EVIDENCE/proofs/wedge_agent_toolcall_001_runner.py
Exits 0 iff the tool fires exactly once (the admitted call) and every adversarial call is
refused with the expected reason and leaves the tool un-fired.
"""

import hashlib
import json
import sys
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.published_source import anchor_sha256, load_record_from_bytes
from IMPLEMENTATION.verifier import verify_envelope, REF_VERIFY_REPLAY

TARGET = "http://tool-server.local/mcp"
GATE_KID = "gate-wedge-demo-001"


def interaction_for(tool, args):
    """Encode a tool call as an admissibility interaction: AP/OP are the authority/operation
    sets the gate evaluates; the tool identity + an args digest ride in the free-form context
    (canon 11.1 C), so the envelope BINDS to this exact tool call."""
    return {
        "AP": ["identity", "role"], "OP": ["session", "request"],
        "context": {"tool": tool, "args_sha256": hashlib.sha256(
            canonical_json(args).encode("utf-8")).hexdigest()},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }


def admit(tool, args):
    """Drive the REAL gate (pep) to admit a tool call; return the signed envelope."""
    captured = {}
    class _R:
        status_code = 200; text = "{}"
    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        captured["headers"] = headers or {}; return _R()
    orig = pep.requests.post
    pep.requests.post = fake_post
    try:
        r = TestClient(pep.app).post("/governed-call",
            json={"target_url": TARGET, "interaction": interaction_for(tool, args)})
        assert r.status_code == 200, r.text
        return r.json()["envelope"]
    finally:
        pep.requests.post = orig


def build_tool_server(state, executed):
    """An MCP-shaped tool server. /mcp handles tools/call; it executes the tool ONLY if the
    admissibility envelope verifies (admitted + bound-to-this-call + current + fresh)."""
    app = FastAPI()
    seen = {}  # decision_id -> True (bounded replay cache; demo-scope)

    @app.post("/mcp")
    async def mcp(request: Request):
        body = await request.json()
        params = body.get("params", {})
        tool, args = params.get("name"), params.get("arguments", {})
        raw = request.headers.get("X-Elyon-Sol-Envelope")
        try:
            envelope = json.loads(raw) if raw is not None else None
        except Exception:
            envelope = None
        # Fetch + anchor-verify the published record for the CURRENT state.
        record = load_record_from_bytes(state["record_bytes"], state["pinned_root"])
        if record is None:
            raise HTTPException(403, {"executed": False, "reason": "REF_TARGET_ANCHOR_MISMATCH"})
        # Reconstruct the expected interaction from the ACTUAL tool call, and verify the
        # envelope binds to it, is current vs the fetched record, and is fresh.
        expected = interaction_for(tool, args)
        res = verify_envelope(envelope, expected, TARGET, record_source=record,
                              pinned_public_keys=state["pinned_keys"])
        if not res["accepted"]:
            raise HTTPException(403, {"executed": False, "reason": res["reason"]})
        # Replay defense (exactly-once over the window): refuse an already-honored
        # decision_id. decision_id is signed (tamper-proof) and stamped by the gate.
        decision_id = envelope.get("decision_id")
        if decision_id is not None:
            if decision_id in seen:
                raise HTTPException(403, {"executed": False, "reason": REF_VERIFY_REPLAY})
            seen[decision_id] = True
        executed.append({"tool": tool, "args": args})   # THE side effect: the tool fires
        return {"jsonrpc": "2.0", "id": body.get("id"),
                "result": {"executed": True, "tool": tool, "reason": res["reason"]}}

    return app


def main():
    authentic = open("EVIDENCE/published_hashes.json", "rb").read()
    # A "post-update" record: the evaluator state moved (drift). Anchor it on its own bytes
    # so the anchor check passes and reassert reaches the evaluator-hash comparison.
    drifted = json.dumps({**json.loads(authentic),
                          "evaluator_sha256": "0" * 64}, sort_keys=True).encode("utf-8")

    priv = Ed25519PrivateKey.generate()
    pep._INJECTED_SIGNING_KEY = (priv, GATE_KID)
    pinned_keys = {GATE_KID: priv.public_key()}

    state = {"record_bytes": authentic, "pinned_root": anchor_sha256(authentic),
             "pinned_keys": pinned_keys}
    executed = []
    client = TestClient(build_tool_server(state, executed))

    def call(tool, args, envelope):
        headers = {}
        if envelope is not None:
            headers["X-Elyon-Sol-Envelope"] = canonical_json(envelope)
        r = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": tool, "arguments": args}}, headers=headers)
        if r.status_code == 200:
            return True, r.json()["result"]["reason"]
        return False, r.json()["detail"]["reason"]

    results = []
    def check(label, got, exp):
        ok = got == exp; results.append(ok)
        print("[%s] %s\n       got=%s expected=%s" % ("PASS" if ok else "FAIL", label, got, exp))

    print("=" * 74)
    print("WEDGE DEMO: agent tool-call admissibility (MCP-shaped) - VL-066 candidate")
    print("=" * 74)

    # 1. Properly admitted tool call -> the tool FIRES.
    env = admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    check("admitted call executes the tool", call("transfer_funds", {"amount": 100, "to": "acct-42"}, env),
          (True, "REASSERTED_AND_BOUND"))
    fired_after_1 = len(executed)

    # 1b. Replay the admitted call within its window -> refused, tool does NOT fire again.
    check("replay of the admitted call refused (exactly-once)",
          call("transfer_funds", {"amount": 100, "to": "acct-42"}, env),
          (False, "REF_VERIFY_REPLAY"))

    # 2. Un-attested call (agent bypasses the gate) -> refused, tool does NOT fire.
    check("un-attested call refused (A1)", call("transfer_funds", {"amount": 100, "to": "acct-42"}, None),
          (False, "REF_VERIFY_ENVELOPE_ABSENT"))

    # 3. Rebound: envelope admitted for transfer used on a DIFFERENT tool -> binding mismatch.
    check("rebind to a different tool refused", call("delete_database", {"db": "prod"}, env),
          (False, "REF_VERIFY_BINDING_MISMATCH"))

    # 3b. Rebound: same tool, DIFFERENT args -> binding mismatch (args digest differs).
    check("rebind to different args refused", call("transfer_funds", {"amount": 999999, "to": "acct-42"}, env),
          (False, "REF_VERIFY_BINDING_MISMATCH"))

    # 4. Drift: the evaluator/policy state moved; the SAME admitted envelope is now invalid.
    state["record_bytes"] = drifted; state["pinned_root"] = anchor_sha256(drifted)
    check("drifted state invalidates the admission", call("transfer_funds", {"amount": 100, "to": "acct-42"}, env),
          (False, "REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED"))
    state["record_bytes"] = authentic; state["pinned_root"] = anchor_sha256(authentic)

    # 5. Stale: an admission past its decision-freshness window -> refused (uses VL-065).
    pep.DECISION_MAX_AGE_SECONDS = 1
    short_env = admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    pep.DECISION_MAX_AGE_SECONDS = 300
    time.sleep(2)
    check("stale admission refused (past freshness window)",
          call("transfer_funds", {"amount": 100, "to": "acct-42"}, short_env),
          (False, "REF_VERIFY_SIGNATURE_EXPIRED"))

    print("-" * 74)
    acted_once = (len(executed) == 1 and fired_after_1 == 1)
    print("TOOL FIRED EXACTLY ONCE (only the admitted call): %s  (executed=%d)"
          % ("HOLDS" if acted_once else "FAILED", len(executed)))
    ok = all(results) and acted_once
    print("=" * 74)
    print("RESULT:", "WEDGE PROPERTY HOLDS end-to-end on the tool-call surface" if ok
          else "VIOLATION")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
