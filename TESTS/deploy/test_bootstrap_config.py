"""
C1 deploy bootstrap tests (docs/restructure/20_deploy_packaging_spec.md, VL-081).

C1's sandbox-green referent: the generated deployment config is INTERNALLY CONSISTENT - an
envelope signed with the bootstrap signing key, for the bootstrap target_url, is HONORED by the
production verifier against the bootstrap pinned public key + the committed record served at the
bootstrap anchor; a tampered interaction is refused. Plus a structural check that the
docker-compose services name real module entrypoints. The container orchestration itself is NOT
validated here (no docker; AUTHOR stand-up).
"""

import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

import deploy.bootstrap_config as bootstrap
from IMPLEMENTATION.envelope import build_envelope, sign_envelope
from IMPLEMENTATION.evaluator import load_manifest
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.published_source import load_record_from_bytes
from IMPLEMENTATION.verifier import verify_envelope, REF_VERIFY_BINDING_MISMATCH

PUBLISHED = "EVIDENCE/published_hashes.json"


def _signed(config, interaction):
    priv = Ed25519PrivateKey.from_private_bytes(
        bytes.fromhex(config["ELYON_SIGNING_KEY_HEX"])
    )
    env = build_envelope(
        decision="ELIGIBLE",
        target_url=config["ELYON_TARGET_URL"],
        normalized_interaction=interaction,
        manifest=load_manifest(),
        ac3=True, t26=True, manifest_integrity=True,
        timestamp_utc="2026-06-09T00:00:00+00:00",
    )
    return sign_envelope(env, priv, config["ELYON_SIGNING_KEY_ID"],
                         decision_id=uuid.uuid4().hex)


def _verify(config, env, interaction):
    pub = Ed25519PublicKey.from_public_bytes(
        bytes.fromhex(config["ELYON_GATE_PUBLIC_KEY_HEX"])
    )
    record = load_record_from_bytes(open(PUBLISHED, "rb").read(),
                                    config["ELYON_PINNED_ROOT_SHA256"])
    assert record is not None, "bootstrap anchor must match the committed record"
    return verify_envelope(
        env, interaction, config["ELYON_TARGET_URL"],
        record_source=record,
        pinned_public_keys={config["ELYON_GATE_KEY_ID"]: pub},
    )


def test_bootstrap_config_is_internally_consistent():
    config = bootstrap.build_config()
    # The signing id the gate uses equals the id the target pins.
    assert config["ELYON_SIGNING_KEY_ID"] == config["ELYON_GATE_KEY_ID"]
    # The pinned public key corresponds to the signing private key.
    priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(config["ELYON_SIGNING_KEY_HEX"]))
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    assert priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex() == \
        config["ELYON_GATE_PUBLIC_KEY_HEX"]


def test_bootstrap_config_round_trips_admit_verify():
    config = bootstrap.build_config()
    interaction = interaction_for("transfer_funds", {"amount": 100, "to": "acct-42"})
    env = _signed(config, interaction)
    result = _verify(config, env, interaction)
    assert result["accepted"] is True
    assert result["reason"] == "REASSERTED_AND_BOUND"


def test_bootstrap_config_refuses_tampered_interaction():
    config = bootstrap.build_config()
    signed_for = interaction_for("transfer_funds", {"amount": 100, "to": "acct-42"})
    env = _signed(config, signed_for)
    tampered = interaction_for("transfer_funds", {"amount": 999999, "to": "acct-42"})
    result = _verify(config, env, tampered)
    assert result["accepted"] is False
    assert result["reason"] == REF_VERIFY_BINDING_MISMATCH


def test_compose_services_name_real_entrypoints():
    # Dependency-free structural check (no pyyaml in the CI deps): the compose
    # file declares the three services and names each real module:app entrypoint,
    # and each named module actually exposes `app`.
    import importlib

    text = open("deploy/docker-compose.yml").read()
    for service in ("publisher:", "target:", "gate:"):
        assert service in text, service
    for app_ref in ("IMPLEMENTATION.publisher:app",
                    "IMPLEMENTATION.reference_target:app",
                    "IMPLEMENTATION.pep:app"):
        assert app_ref in text, app_ref
        mod = app_ref.split(":")[0]
        assert hasattr(importlib.import_module(mod), "app"), mod
