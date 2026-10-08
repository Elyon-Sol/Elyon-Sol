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


# ---------------------------------------------------------------------------
# .env file mode (VL-154 open item): the file holds the gate's private signing
# key and must not be readable by other local accounts.
# ---------------------------------------------------------------------------

import os
import stat

import pytest

_posix_only = pytest.mark.skipif(os.name != "posix", reason="POSIX file modes")


@_posix_only
def test_env_file_is_created_owner_only(tmp_path):
    """A fresh .env is 0600 regardless of the process umask (a permissive umask
    is exactly the case the explicit mode exists for)."""
    out = tmp_path / ".env"
    old_umask = os.umask(0o000)
    try:
        bootstrap.write_env(str(out), bootstrap.build_config())
    finally:
        os.umask(old_umask)
    assert stat.S_IMODE(out.stat().st_mode) == 0o600
    assert "ELYON_SIGNING_KEY_HEX=" in out.read_text()


@_posix_only
def test_existing_world_readable_env_is_tightened_before_writing(tmp_path):
    """O_CREAT's mode applies only to a new file: an operator's pre-existing
    0644 .env must be tightened, not inherited, before the key lands in it."""
    out = tmp_path / ".env"
    out.write_text("stale\n")
    out.chmod(0o644)
    bootstrap.write_env(str(out), bootstrap.build_config())
    assert stat.S_IMODE(out.stat().st_mode) == 0o600
    assert "stale" not in out.read_text()


def test_main_writes_through_write_env(monkeypatch, tmp_path):
    """main() reaches the file only through write_env (no second, unguarded
    open path)."""
    seen = {}

    def spy(path, config):
        seen["path"] = path
        seen["keys"] = set(config)

    monkeypatch.setattr(bootstrap, "write_env", spy)
    monkeypatch.setattr(bootstrap, "__file__", str(tmp_path / "bootstrap_config.py"))
    bootstrap.main()
    assert seen["path"] == str(tmp_path / ".env")
    assert "ELYON_SIGNING_KEY_HEX" in seen["keys"]


# ---------------------------------------------------------------------------
# Published ports in the authz overlay (VL-154 open item). Dependency-free
# structural check (no pyyaml in the CI deps), like the entrypoint check above.
# ---------------------------------------------------------------------------

def _compose_service_blocks(text):
    """Split a compose file's `services:` section into {name: [lines]} by the
    two-space service indentation."""
    blocks, current = {}, None
    in_services = False
    for line in text.splitlines():
        if line.startswith("services:"):
            in_services = True
            continue
        if not in_services or not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and not line.startswith("   ") and line.rstrip().endswith(":"):
            current = line.strip()[:-1]
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)
    return blocks


def _published_ports(block_lines):
    ports, in_ports = [], False
    for line in block_lines:
        stripped = line.strip()
        if stripped == "ports:":
            in_ports = True
            continue
        if in_ports:
            if stripped.startswith("- "):
                ports.append(stripped[2:].split("#")[0].strip().strip('"').strip("'"))
                continue
            if stripped.startswith("#"):
                continue
            in_ports = False
    return ports


def test_authz_overlay_publishes_sidecar_on_loopback_and_opa_not_at_all():
    """The sidecar's decision endpoint must not be reachable from the LAN by
    default (ALLOW/DENY and its refusal codes are an oracle), and OPA's
    ext-authz gRPC port is for Envoy on the compose network only. Envoy's
    listener is the one intended public surface."""
    blocks = _compose_service_blocks(open("deploy/docker-compose.authz.yml").read())
    assert {"elyon-authz", "envoy", "opa", "upstream"} <= set(blocks)

    sidecar_ports = _published_ports(blocks["elyon-authz"])
    assert sidecar_ports, "the walkthrough reaches the sidecar on the host"
    for p in sidecar_ports:
        assert p.startswith("${ELYON_AUTHZ_BIND:-127.0.0.1}:"), p

    assert _published_ports(blocks["opa"]) == []
    assert _published_ports(blocks["upstream"]) == []
    assert _published_ports(blocks["envoy"]) == ["10000:10000"]


# ---------------------------------------------------------------------------
# Image pins (VL-154 open item): every image the deployment pulls is pinned by
# digest, with an exact (non-floating) tag as its label.
# ---------------------------------------------------------------------------

import glob
import re

_DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")


def _image_refs():
    refs = []
    for path in sorted(glob.glob("deploy/docker-compose*.yml")):
        for line in open(path):
            m = re.match(r"\s*image:\s*(\S+)", line)
            if m:
                refs.append((path, m.group(1)))
    for line in open("deploy/Dockerfile"):
        m = re.match(r"FROM\s+(\S+)", line)
        if m:
            refs.append(("deploy/Dockerfile", m.group(1)))
    return refs


def test_every_pulled_image_is_pinned_by_digest_with_an_exact_tag():
    refs = _image_refs()
    assert len(refs) >= 5, refs  # envoy, opa, two redis, the python base
    for path, ref in refs:
        assert _DIGEST.search(ref), f"{path}: {ref} has no digest"
        tag = ref.split("@")[0].rsplit(":", 1)[-1]
        assert "latest" not in tag, f"{path}: {ref} uses a floating tag"
