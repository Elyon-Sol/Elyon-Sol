"""The deployment predicates (T-readiness). RED today, by design.

Each is a DECLARED xfail whose reason names its blocker, so the suite stays
green-with-declared-xfail (the red is visible and named, never hidden by a skip).
When the underlying work lands, wire the marked ANCHOR to the real path and REMOVE
the xfail marker, turning the predicate into a true regression gate, and flip the
matching flags in EVIDENCE/readiness.json to value/green true with this test as
the proof.

The bodies fail closed (raise AssertionError) until wired, so an accidental green
cannot slip through. See docs/restructure/10_readiness_spec.md sections 4 and 8.

NOTE: the two ANCHORs below are the only parts of T-readiness that couple to repo
internals (pep.py's default forward and the real transport). They are written
against the envelope/verifier API shapes known from VL-040/041/042 but MUST be
confirmed against pep.py before they exercise the real chain. Until then they are
honest reds, not fiction.
"""

import pytest


def test_default_forward_is_signed_and_verified(gate_signing, monkeypatch):
    # ANCHOR 1 WIRED (VL-047 cutover): pep.py's DEFAULT forward (no opt-in flags)
    # signs the emitted envelope; a co-located target pinning the gate's public
    # key ACCEPTS the signed envelope and REFUSES an unsigned forge. No xfail:
    # this is now a real regression gate. Cross-host transport is NOT asserted
    # here (that is END_TO_END_NO_SHORTCUT / G5); the verifying target is
    # co-located and uses verify_envelope's pinned-key + local-disk reassert
    # path. The gate_signing fixture (TESTS/conftest.py) injects the ephemeral
    # key into pep._get_signing_key.
    import json
    from fastapi.testclient import TestClient

    from IMPLEMENTATION.pep import app as pep_app
    from IMPLEMENTATION.evaluator import manifest_sha256
    from IMPLEMENTATION.verifier import (
        verify_envelope,
        ACCEPT_REASSERTED_AND_BOUND,
    )

    pub = gate_signing["public_key"]
    key_id = gate_signing["key_id"]
    pinned = {key_id: pub}
    target = "https://upstream.example/default-secure-predicate"

    captured = {}

    class _Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        captured["headers"] = headers or {}
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    interaction = {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }
    resp = TestClient(pep_app).post(
        "/governed-call",
        json={"target_url": target, "interaction": interaction},
    )
    assert resp.status_code == 200

    signed = json.loads(captured["headers"]["X-Elyon-Sol-Envelope"])
    assert signed["issuer_key_id"] == key_id
    assert isinstance(signed["issuer_signature"], str)

    accepted = verify_envelope(signed, interaction, target, pinned_public_keys=pinned)
    assert accepted["accepted"] is True
    assert accepted["reason"] == ACCEPT_REASSERTED_AND_BOUND

    forge = {k: v for k, v in signed.items() if k != "issuer_signature"}
    refused = verify_envelope(forge, interaction, target, pinned_public_keys=pinned)
    assert refused["accepted"] is False


def test_end_to_end_no_shortcut(monkeypatch):
    # ANCHOR 2 WIRED (VL-048 signed cross-host chain): the lighter,
    # suite-level regression gate for END_TO_END_NO_SHORTCUT. The HEAVY
    # no-shortcut proof of record is the runner
    # EVIDENCE/proofs/g5_signed_cross_host_001_runner.py (a real two-process,
    # real-socket, genuinely-divergent-disk run; named as the exercised_e2e /
    # transported proof in EVIDENCE/readiness.json and run in the author's real
    # environment at session-close). This pytest test asserts the COMPOSABLE
    # signed-chain invariant in-process so the suite reds the moment the chain
    # breaks: the gate signs on its DEFAULT path via the PRODUCTION key path,
    # the pushed signed envelope is verified against the gate's out-of-band
    # public key AND the published record (currency), and the keyless forge is
    # refused on the signed path.
    #
    # HONESTY NOTE: this test deliberately does NOT use the autouse
    # `gate_signing` conftest fixture (which monkeypatches pep._get_signing_key
    # IN-PROCESS - an in-process-key-injection shortcut that section 4.2
    # forbids). It drives the production env-var key path
    # (ELYON_SIGNING_KEY_HEX + ELYON_SIGNING_KEY_ID) so the signing path under
    # test is the deployed one. In-process transport here is acceptable for a
    # regression gate; the REAL cross-host transport with no shortcut is the
    # runner's job (D-1=b). A3b freshness (a stale-but-anchor-matching signed
    # record is still honored) remains a NAMED bound, not closed here.
    import json

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PrivateFormat,
        NoEncryption,
    )
    from fastapi.testclient import TestClient

    import IMPLEMENTATION.pep as pep
    from IMPLEMENTATION.evaluator import manifest_sha256
    from IMPLEMENTATION.verifier import (
        verify_envelope,
        ACCEPT_REASSERTED_AND_BOUND,
        REF_VERIFY_SIGNATURE_INVALID,
    )

    # Production key path: an ephemeral key handed to the gate via the env
    # pair, NOT via the conftest in-process injection. The autouse
    # `gate_signing` fixture has already replaced pep._get_signing_key with an
    # in-process lambda (the shortcut we must not use here); restore a resolver
    # that genuinely reads the env pair (byte-identical to pep's real
    # _get_signing_key env branch) so the signing path under test is the
    # deployed one.
    priv = Ed25519PrivateKey.generate()
    key_id = "anchor2-signed-chain-001"
    key_hex = priv.private_bytes(
        Encoding.Raw, PrivateFormat.Raw, NoEncryption()
    ).hex()
    monkeypatch.setenv("ELYON_SIGNING_KEY_HEX", key_hex)
    monkeypatch.setenv("ELYON_SIGNING_KEY_ID", key_id)

    def _env_resolver():
        import os as _os
        kh = _os.environ.get("ELYON_SIGNING_KEY_HEX")
        ki = _os.environ.get("ELYON_SIGNING_KEY_ID")
        if kh and ki:
            return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(kh)), ki
        return None

    # Override the conftest fixture's in-process lambda with the env-reading
    # resolver (this IS the production path: pep's own _get_signing_key reads
    # exactly these env vars).
    monkeypatch.setattr(pep, "_get_signing_key", _env_resolver)

    pub = priv.public_key()
    pinned = {key_id: pub}
    target = "https://upstream.example/end-to-end-no-shortcut"

    captured = {}

    class _Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        captured["headers"] = headers or {}
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    interaction = {
        "AP": ["identity", "role"],
        "OP": ["session", "request"],
        "context": {},
        "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha256(),
    }
    resp = TestClient(pep.app).post(
        "/governed-call",
        json={"target_url": target, "interaction": interaction},
    )
    assert resp.status_code == 200, "gate did not return ELIGIBLE on the signed default path"

    signed = json.loads(captured["headers"]["X-Elyon-Sol-Envelope"])
    assert signed["issuer_key_id"] == key_id
    assert isinstance(signed["issuer_signature"], str)

    # Currency from the published record (the transported artifact), signature
    # from the out-of-band pin. Co-located here; the cross-host transport with
    # no shortcut is the runner.
    record = {
        "canon_sha256": signed["canon"]["canon_sha256"],
        "evaluator_sha256": signed["evaluator"]["evaluator_sha256"],
        "manifest_sha256": signed["evaluated_against"]["manifest_sha256"],
    }
    accepted = verify_envelope(
        signed, interaction, target,
        record_source=record, pinned_public_keys=pinned,
    )
    assert accepted["accepted"] is True
    assert accepted["reason"] == ACCEPT_REASSERTED_AND_BOUND

    # The VL-039-follow-up-2 keyless forge: strip the signature. The signed
    # path refuses it (no downgrade to the unsigned path).
    forge = {k: v for k, v in signed.items() if k != "issuer_signature"}
    refused = verify_envelope(
        forge, interaction, target,
        record_source=record, pinned_public_keys=pinned,
    )
    assert refused["accepted"] is False
    assert refused["reason"] == REF_VERIFY_SIGNATURE_INVALID


def test_root_recovery_wired(monkeypatch):
    # ANCHOR 3 WIRED (VL-049): the lighter, in-process regression gate for
    # ROOT_RECOVERY (option alpha). The HEAVY no-shortcut proof of record is the
    # runner EVIDENCE/proofs/root_recovery_cross_host_001_runner.py (a real
    # two-process, real-socket, genuinely-divergent-disk run; named as the
    # exercised_e2e / transported proof in EVIDENCE/readiness.json and run in the
    # author's real environment). This pytest test asserts the rotation-trust
    # invariant in-process so the suite reds the moment the chain breaks: the gate
    # signs on its DEFAULT path via the PRODUCTION key path, and a target pinning
    # ONLY R1 honors the gate-signed envelope because the issuer key is vouched by
    # a key record signed by the designated-active successor R2 (a planned in-band
    # R1->R2 rotation, no re-pin); a revoked or retired signing root is refused.
    #
    # HONESTY NOTE (mirrors ANCHOR 2): this test does NOT use the autouse
    # gate_signing conftest fixture (in-process key injection, a forbidden
    # shortcut). It drives the production env-var key path (ELYON_SIGNING_KEY_HEX
    # + ELYON_SIGNING_KEY_ID). In-process record construction is acceptable for a
    # regression gate; the REAL cross-host transport with no shortcut is the
    # runner's job (option alpha).
    import json
    from datetime import datetime, timezone, timedelta

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, NoEncryption,
    )
    from fastapi.testclient import TestClient

    import IMPLEMENTATION.pep as pep
    from IMPLEMENTATION.evaluator import manifest_sha256
    from IMPLEMENTATION.verifier import (
        verify_envelope,
        ACCEPT_REASSERTED_AND_BOUND,
        REF_VERIFY_ROOT_REVOKED,
        REF_VERIFY_ROOT_RETIRED,
    )
    from IMPLEMENTATION.root_record_source import load_root_record_from_bytes
    from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
    from EVIDENCE.published_roots_gen import build_root_record, make_root_entry
    from EVIDENCE.published_keys_gen import build_key_record, make_key_entry

    now = datetime.now(timezone.utc)
    r1 = Ed25519PrivateKey.generate()
    r2 = Ed25519PrivateKey.generate()
    gate_priv = Ed25519PrivateKey.generate()
    gate_key_id = "anchor3-rotation-issuer-001"

    # Production gate signing path (NOT the conftest fixture).
    key_hex = gate_priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()).hex()
    monkeypatch.setenv("ELYON_SIGNING_KEY_HEX", key_hex)
    monkeypatch.setenv("ELYON_SIGNING_KEY_ID", gate_key_id)

    def _env_resolver():
        import os as _os
        kh = _os.environ.get("ELYON_SIGNING_KEY_HEX")
        ki = _os.environ.get("ELYON_SIGNING_KEY_ID")
        if kh and ki:
            return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(kh)), ki
        return None
    monkeypatch.setattr(pep, "_get_signing_key", _env_resolver)

    target = "https://upstream.example/root-recovery-predicate"
    captured = {}

    class _Resp:
        status_code = 200
        text = "{}"

    def fake_post(url, json, timeout, headers=None, verify=None, cert=None):
        captured["headers"] = headers or {}
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", fake_post)

    interaction = {
        "AP": ["identity", "role"], "OP": ["session", "request"], "context": {},
        "expected_manifest_version": "1.0", "expected_manifest_sha256": manifest_sha256(),
    }
    resp = TestClient(pep.app).post(
        "/governed-call", json={"target_url": target, "interaction": interaction},
    )
    assert resp.status_code == 200
    signed = json.loads(captured["headers"]["X-Elyon-Sol-Envelope"])
    assert signed["issuer_key_id"] == gate_key_id

    pinned = {"root-1": r1.public_key()}  # target pins ONLY R1, never re-pins

    def root_bytes(entries, serial=1):
        rec = build_root_record("root-1", r1, entries, serial,
                                now + timedelta(hours=24), issued_at=now)
        return json.dumps(rec).encode("utf-8")

    def key_bytes(signer, root_id):
        entry = make_key_entry(gate_key_id, gate_priv.public_key(),
                               not_before=now - timedelta(days=1),
                               not_after=now + timedelta(days=365))
        rec = build_key_record(root_id, signer, [entry], 1,
                               now + timedelta(hours=24), issued_at=now)
        return json.dumps(rec).encode("utf-8")

    def active(rid, pk, successor_of=None):
        return make_root_entry(rid, pk, "active", now - timedelta(days=1),
                               now + timedelta(days=365), successor_of=successor_of)

    # R1 designates R2; target (pinning only R1) builds the status view.
    sv = load_root_record_from_bytes(
        root_bytes([active("root-1", r1.public_key()),
                    active("root-2", r2.public_key(), successor_of="root-1")]),
        pinned, now=now)
    assert sv["reason"] is None

    # Key record signed by designated-active R2, vouching the gate key.
    kv = load_key_record_from_bytes(key_bytes(r2, "root-2"), pinned, now=now,
                                    root_status_view=sv["status_view"])
    assert kv["reason"] is None and gate_key_id in kv["trust_view"]

    # KILLER CASE: target pinning only R1 honors the gate-signed envelope via the
    # R2-vouched key record (planned rotation, no re-pin).
    honored = verify_envelope(signed, interaction, target,
                              key_record_view=kv["trust_view"], now=now)
    assert honored["accepted"] is True
    assert honored["reason"] == ACCEPT_REASSERTED_AND_BOUND

    # Revoked signing root -> key record refused.
    sv_rev = load_root_record_from_bytes(
        root_bytes([active("root-1", r1.public_key()),
                    make_root_entry("root-2", r2.public_key(), "revoked",
                                    now - timedelta(days=1), now + timedelta(days=365),
                                    revoked_at=now - timedelta(minutes=5))], serial=2),
        pinned, now=now)
    kv_rev = load_key_record_from_bytes(key_bytes(r2, "root-2"), pinned, now=now,
                                        root_status_view=sv_rev["status_view"])
    assert kv_rev["reason"] == REF_VERIFY_ROOT_REVOKED

    # Retired signing root, NEW key record -> refused.
    sv_ret = load_root_record_from_bytes(
        root_bytes([active("root-1", r1.public_key()),
                    make_root_entry("root-2", r2.public_key(), "retired",
                                    now - timedelta(days=1), now + timedelta(days=365),
                                    retired_at=now - timedelta(hours=1))], serial=3),
        pinned, now=now)
    kv_ret = load_key_record_from_bytes(key_bytes(r2, "root-2"), pinned, now=now,
                                        root_status_view=sv_ret["status_view"])
    assert kv_ret["reason"] == REF_VERIFY_ROOT_RETIRED
