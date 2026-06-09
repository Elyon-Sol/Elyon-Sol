"""
Attack harness (docs/restructure/19_attack_harness_and_claim_sheet_spec.md, increment VL-079, C3).

Turns `external_verification_readiness.md` gate 2 (the falsifiable claim sheet) into RUNNABLE
attacks. Each attack restates a bounded claim as a break-it challenge with a pass/fail criterion;
an attack PASSES when it is DEFEATED (the surface refuses with the expected reason), and the
positive control passes when a valid call IS honored.

The attacks run against a pluggable `Surface`, so the SAME suite runs in-process now (the
`InProcessSurface` over the VL-078 ExecutorGate) and against a real deployed surface later (the
`HttpSurface` over a reference-target URL - the seam C1/C2 plug into). HONEST CEILING (gate 2):
defeating the attacks against the in-process surface proves they are well-formed and the gate
refuses them locally; it is NOT external validation. The claim sheet stays referent-incomplete
until gate 1 (real cross-host transport) provides a genuine surface to attack. No in-process pass
moves the external-validation axis.

The harness only OBSERVES: it adds no decision and no reason code (every expected reason is a
production REF_*). Build-then-wire: new file, no default-path caller; the gate is byte-unchanged.
"""

import time
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.executor_sdk import ExecutorGate
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_SIGNATURE_INVALID,
    REF_VERIFY_BINDING_MISMATCH,
    REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED,
    REF_VERIFY_SIGNATURE_EXPIRED,
    REF_VERIFY_REPLAY,
)

TOOL = "transfer_funds"
ARGS = {"amount": 100, "to": "acct-42"}


class AttackResult(NamedTuple):
    id: str
    challenge: str
    honored: bool
    reason: str
    expect_honored: bool
    expect_reason: Optional[str]
    passed: bool


# --------------------------------------------------------------------------
# Surfaces (admit a decision; attempt a tool call -> honored/reason)
# --------------------------------------------------------------------------

class InProcessSurface:
    """Drives the production gate (pep) to admit, and the VL-078 ExecutorGate to attempt. One
    persistent ExecutorGate per surface, so its replay cache survives across attempts (the replay
    attack needs that). Supply either a gate_private_key to inject into pep (standalone runner) or
    a gate_public_key to pin while pep's signing key is provided elsewhere (test conftest)."""

    def __init__(self, *, target_id, record_bytes, gate_key_id,
                 gate_private_key=None, gate_public_key=None):
        from fastapi.testclient import TestClient

        if gate_private_key is not None:
            pep._INJECTED_SIGNING_KEY = (gate_private_key, gate_key_id)
            gate_public_key = gate_private_key.public_key()
        if gate_public_key is None:
            raise ValueError("supply gate_private_key or gate_public_key")
        self.target_id = target_id
        self._client = TestClient(pep.app)
        self._gate = ExecutorGate(
            pinned_public_keys={gate_key_id: gate_public_key},
            target_id=target_id,
            record_bytes=record_bytes,
        )

    def admit(self, tool, args, *, max_age=300, target_url=None):
        class _R:
            status_code = 200
            text = "{}"

        def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
            return _R()

        prev_age, prev_post = pep.DECISION_MAX_AGE_SECONDS, pep.requests.post
        pep.DECISION_MAX_AGE_SECONDS = max_age
        pep.requests.post = fake_post
        try:
            r = self._client.post(
                "/governed-call",
                json={"target_url": target_url or self.target_id,
                      "interaction": interaction_for(tool, args)},
            )
            assert r.status_code == 200, r.text
            return r.json()["envelope"]
        finally:
            pep.DECISION_MAX_AGE_SECONDS = prev_age
            pep.requests.post = prev_post

    def attempt(self, tool, args, envelope) -> Tuple[bool, str]:
        d = self._gate.check(envelope, interaction_for(tool, args))
        return d.honored, d.reason


class HttpSurface:
    """Drives a gate URL to admit and a reference-target URL to attempt, over real HTTP. The
    AUTHOR adapter: against a real cross-host deployment (C1/C2) it runs the SAME attacks over real
    transport. `gate_client` / `target_client` are anything with `.post(path, json=, headers=)`
    returning a response with `.status_code` and `.json()` - a fastapi TestClient (the shape test)
    or a RequestsClient (a real host). max_age is a gate deploy-config concern over HTTP, so the
    stale attack is not driven here (it is covered in-process)."""

    def __init__(self, gate_client, target_client, target_url):
        self.gate_client = gate_client
        self.target_client = target_client
        self.target_url = target_url

    def admit(self, tool, args, *, max_age=300, target_url=None):
        r = self.gate_client.post(
            "/governed-call",
            json={"target_url": target_url or self.target_url,
                  "interaction": interaction_for(tool, args)},
        )
        return r.json()["envelope"]

    def attempt(self, tool, args, envelope) -> Tuple[bool, str]:
        headers = {}
        if envelope is not None:
            headers["X-Elyon-Sol-Envelope"] = canonical_json(envelope)
        r = self.target_client.post("/target", json=interaction_for(tool, args), headers=headers)
        if r.status_code == 200:
            body = r.json()
            return body["honored"], body["reason"]
        return False, r.json()["detail"]["reason"]


class RequestsClient:
    """Minimal `.post` shim over `requests` for a real host (AUTHOR). Not exercised in-sandbox.
    `verify` is the requests TLS-verification argument: a CA bundle path (real TLS, the C2 case),
    True (system store / a public CA), or False (NEVER for a real run - verification off defeats
    the point). Defaults to True (fail-closed: an unverifiable peer raises)."""

    def __init__(self, base_url, verify=True):
        self.base_url = base_url.rstrip("/")
        self.verify = verify

    def post(self, path, json=None, headers=None):
        import requests

        return requests.post(self.base_url + path, json=json, headers=headers or {},
                             verify=self.verify, timeout=10)


# --------------------------------------------------------------------------
# The attack suite (gate-2 break-it challenges)
# --------------------------------------------------------------------------

def run_suite(surface, drifted_surface=None, include_stale=True) -> List[AttackResult]:
    """Run the attack suite against `surface`. `drifted_surface` (a surface whose executor sees a
    re-published / drifted state) drives the drift attack; if None it is skipped. `include_stale`
    drives the stale attack, which needs control of the gate's decision window (admit max_age) -
    set it False for a surface that cannot control that (the live HTTP adapter, where the gate's
    window is fixed deploy config). Returns one AttackResult per attack."""
    results: List[AttackResult] = []

    def record(id_, challenge, got, expect_honored, expect_reason):
        honored, reason = got
        passed = (honored == expect_honored) and (
            expect_reason is None or reason == expect_reason
        )
        results.append(AttackResult(id_, challenge, honored, reason,
                                    expect_honored, expect_reason, passed))

    # Positive control: a valid admitted call IS honored (else "all refused" is vacuous).
    env = surface.admit(TOOL, ARGS)
    record("positive_control", "a valid admitted call is honored",
           surface.attempt(TOOL, ARGS, env), True, "REASSERTED_AND_BOUND")

    # A1 / un-attested: reach the executor with no envelope.
    record("unattested", "reach the target with no admissibility envelope (A1)",
           surface.attempt(TOOL, ARGS, None), False, REF_VERIFY_ENVELOPE_ABSENT)

    # Forge: tamper a signed field of a real envelope.
    forged = dict(surface.admit(TOOL, ARGS))
    forged["decision_id"] = "forged-" + str(forged.get("decision_id"))
    record("forged_signature", "tamper a signed field; pass off a forged envelope",
           surface.attempt(TOOL, ARGS, forged), False, REF_VERIFY_SIGNATURE_INVALID)

    # Replay: present the same admitted envelope twice.
    env_r = surface.admit(TOOL, ARGS)
    surface.attempt(TOOL, ARGS, env_r)  # first: honored
    record("replay", "present the same admitted envelope twice (exactly-once)",
           surface.attempt(TOOL, ARGS, env_r), False, REF_VERIFY_REPLAY)

    # Rebind to a different tool.
    record("rebind_tool", "use a transfer envelope to authorize delete_database",
           surface.attempt("delete_database", {"db": "prod"}, surface.admit(TOOL, ARGS)),
           False, REF_VERIFY_BINDING_MISMATCH)

    # Rebind to different args.
    record("rebind_args", "use the envelope with different (larger) args",
           surface.attempt(TOOL, {"amount": 999999, "to": "acct-42"}, surface.admit(TOOL, ARGS)),
           False, REF_VERIFY_BINDING_MISMATCH)

    # Target-URL swap: an envelope bound to target A presented to target B.
    env_swap = surface.admit(TOOL, ARGS, target_url="mcp://elyon-sol/OTHER-surface")
    record("target_url_swap", "present an envelope bound to another target",
           surface.attempt(TOOL, ARGS, env_swap), False, REF_VERIFY_BINDING_MISMATCH)

    # Drift: the executor's published/evaluator state moved.
    if drifted_surface is not None:
        env_d = surface.admit(TOOL, ARGS)
        record("drifted_state", "mint acceptance against a byte-divergent / re-published state",
               drifted_surface.attempt(TOOL, ARGS, env_d), False,
               REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED)

    # Stale: an admission presented past its freshness window (needs admit-window control).
    if include_stale:
        env_s = surface.admit(TOOL, ARGS, max_age=1)
        time.sleep(2)
        record("stale", "replay an admission past its decision-freshness window",
               surface.attempt(TOOL, ARGS, env_s), False, REF_VERIFY_SIGNATURE_EXPIRED)

    return results
