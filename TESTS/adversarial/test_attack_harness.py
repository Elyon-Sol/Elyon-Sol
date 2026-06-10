"""
Attack harness tests (docs/restructure/19_attack_harness_and_claim_sheet_spec.md, VL-079, C3).

Prove the gate-2 attack suite is defeated against the in-process surface, and that the HttpSurface
adapter (the seam a real cross-host surface plugs into) drives a real HTTP reference target. A
green run here is NOT external validation (gate 2): it proves the attacks are well-formed and the
gate refuses them; the real-transport run is the author's (gate 1 / C1+C2).
"""

from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.published_source import anchor_sha256, load_record_from_bytes
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.reference_target import build_reference_target_app
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ENVELOPE_ABSENT,
    REF_VERIFY_BINDING_MISMATCH,
)
from EVIDENCE.proofs.attack_harness import InProcessSurface, HttpSurface, run_suite

TARGET_ID = "mcp://elyon-sol/tool-server"
HTTP_TARGET_URL = "http://tool-server.test/target"


def _published():
    return open("EVIDENCE/published_hashes.json", "rb").read()


def test_all_attacks_defeated_in_process(gate_signing):
    import json
    authentic = _published()
    drifted = json.dumps({**json.loads(authentic), "evaluator_sha256": "0" * 64},
                         sort_keys=True).encode("utf-8")
    surface = InProcessSurface(
        target_id=TARGET_ID, record_bytes=authentic,
        gate_key_id=gate_signing["key_id"], gate_public_key=gate_signing["public_key"],
    )
    drifted_surface = InProcessSurface(
        target_id=TARGET_ID, record_bytes=drifted,
        gate_key_id=gate_signing["key_id"], gate_public_key=gate_signing["public_key"],
    )
    results = run_suite(surface, drifted_surface=drifted_surface)
    failed = [r for r in results if not r.passed]
    assert not failed, failed
    assert any(r.id == "positive_control" and r.honored for r in results)
    assert len([r for r in results if r.id != "positive_control"]) == 8


def _reference_target_client(gate_signing):
    pub_app = FastAPI()

    @pub_app.get("/published_hashes.json")
    async def published():
        return Response(content=_published(), media_type="application/json")

    pub_client = TestClient(pub_app)

    def fetch(url, pinned_root):
        resp = pub_client.get("/published_hashes.json")
        if resp.status_code != 200:
            return None
        return load_record_from_bytes(resp.content, pinned_root)

    config = {
        "target_url": HTTP_TARGET_URL,
        "publisher_url": "http://publisher.test/published_hashes.json",
        "pinned_root_sha256": anchor_sha256(_published()),
        "pinned_public_keys": {gate_signing["key_id"]: gate_signing["public_key"]},
    }
    app = build_reference_target_app(config_provider=lambda: config, fetch=fetch)
    return TestClient(app)


def test_http_surface_drives_real_reference_target(gate_signing, monkeypatch):
    # The gate forwards upstream via requests.post on ELIGIBLE; in this test the
    # target is a TestClient (not reachable over real HTTP at HTTP_TARGET_URL), so
    # neutralize the forward to keep the test hermetic. pep and transport share the
    # one requests module object, so patching requests.post here covers both. The
    # attack harness presents the returned envelope to target_client directly.
    class _R:
        status_code = 200
        text = "{}"

    monkeypatch.setattr(pep.requests, "post",
                        lambda *a, **k: _R())
    surface = HttpSurface(
        gate_client=TestClient(pep.app),
        target_client=_reference_target_client(gate_signing),
        target_url=HTTP_TARGET_URL,
    )
    # Positive control over real HTTP: a valid admitted call is honored.
    env = surface.admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    honored, reason = surface.attempt("transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert honored is True and reason == "REASSERTED_AND_BOUND"
    # Un-attested over real HTTP.
    h2, r2 = surface.attempt("transfer_funds", {"amount": 100, "to": "acct-42"}, None)
    assert h2 is False and r2 == REF_VERIFY_ENVELOPE_ABSENT
    # Rebind over real HTTP.
    h3, r3 = surface.attempt("delete_database", {"db": "prod"}, env)
    assert h3 is False and r3 == REF_VERIFY_BINDING_MISMATCH


def test_live_suite_subset_defeated_over_http(gate_signing, monkeypatch):
    # The exact suite call the live runner makes (include_stale=False, no drifted
    # surface), validated over an in-process HttpSurface. Proves the live runner's
    # suite logic; the real-transport run is the author's (gate 1).
    class _R:
        status_code = 200
        text = "{}"

    monkeypatch.setattr(pep.requests, "post", lambda *a, **k: _R())
    surface = HttpSurface(
        gate_client=TestClient(pep.app),
        target_client=_reference_target_client(gate_signing),
        target_url=HTTP_TARGET_URL,
    )
    results = run_suite(surface, drifted_surface=None, include_stale=False)
    failed = [r for r in results if not r.passed]
    assert not failed, failed
    ids = {r.id for r in results}
    assert "stale" not in ids and "drifted_state" not in ids
    assert "positive_control" in ids and "target_url_swap" in ids
    assert len([r for r in results if r.id != "positive_control"]) == 6


def test_live_runner_unconfigured_exits_2(monkeypatch):
    for var in ("ELYON_LIVE_GATE_URL", "ELYON_LIVE_TARGET_URL", "ELYON_LIVE_TARGET_ID"):
        monkeypatch.delenv(var, raising=False)
    import importlib
    runner = importlib.import_module("EVIDENCE.proofs.attack_suite_live_runner")
    import pytest
    with pytest.raises(SystemExit) as exc:
        runner.main()
    assert exc.value.code == 2


def test_http_surface_acted_count_reads_received(gate_signing, monkeypatch):
    # The push positive control reads the target's /received count via acted_count(); validate the
    # plumbing (the full push path - the gate actually forwarding - is validated by the live run).
    class _R:
        status_code = 200
        text = "{}"

    monkeypatch.setattr(pep.requests, "post", lambda *a, **k: _R())
    surface = HttpSurface(
        gate_client=TestClient(pep.app),
        target_client=_reference_target_client(gate_signing),
        target_url=HTTP_TARGET_URL,
    )
    assert surface.acted_count() == 0
    env = surface.admit("transfer_funds", {"amount": 100, "to": "acct-42"})
    honored, _ = surface.attempt("transfer_funds", {"amount": 100, "to": "acct-42"}, env)
    assert honored is True
    assert surface.acted_count() == 1   # the target acted -> /received incremented
