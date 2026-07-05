"""
Typed-impact WIRING (step 8.2): the request schema carries an OPTIONAL
interaction_type, and interaction_for derives per-type AP/OP under a typed
manifest while staying BYTE-IDENTICAL under the flat/default manifest.
"""

import hashlib
import json

import IMPLEMENTATION.mcp_server as mcp
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.evaluator import manifest_sha256
from IMPLEMENTATION.request_validator import (
    validate_request, REF_SCHEMA_TYPE_MISMATCH,
)

TYPED = {
    "version": "1.1", "interaction_type": "default",
    "AR": ["identity", "role"], "R": ["session", "request"],
    "HIGH_IMPACT": ["role", "request"],
    "interaction_types": {
        "read": {"AR": ["identity"], "R": ["session"], "high_impact": False},
        "transfer": {"AR": ["identity", "role"], "R": ["session", "request"],
                     "high_impact": True},
    },
}


def _install_typed(monkeypatch):
    sha = hashlib.sha256(json.dumps(TYPED, sort_keys=True).encode()).hexdigest()
    monkeypatch.setattr(mcp, "load_manifest", lambda: dict(TYPED))
    monkeypatch.setattr(mcp, "manifest_sha256", lambda *a, **k: sha)
    return sha


# ---- interaction_for byte-identity under the flat/default manifest --------

def test_interaction_for_flat_byte_identical_REVERT_CATCHER():
    """star: under the real flat manifest interaction_for is UNCHANGED - full
    tokens, version 1.0, NO interaction_type field - for ANY tool."""
    for tool in ("read", "transfer_funds", "anything_else"):
        i = interaction_for(tool, {"a": 1})
        assert i["AP"] == ["identity", "role"]
        assert i["OP"] == ["session", "request"]
        assert "interaction_type" not in i
        assert i["expected_manifest_version"] == "1.0"
        assert i["expected_manifest_sha256"] == manifest_sha256()


# ---- interaction_for per-type under a typed manifest ----------------------

def test_interaction_for_typed_benign(monkeypatch):
    _install_typed(monkeypatch)
    i = interaction_for("read", {"a": 1})
    assert set(i["AP"]) == {"identity"} and set(i["OP"]) == {"session"}
    assert i["interaction_type"] == "read"


def test_interaction_for_typed_sensitive(monkeypatch):
    _install_typed(monkeypatch)
    i = interaction_for("transfer_funds", {"amount": 100})
    assert set(i["AP"]) == {"identity", "role"} and set(i["OP"]) == {"session", "request"}
    assert i["interaction_type"] == "transfer"


def test_interaction_for_typed_unknown_tool_is_conservative(monkeypatch):
    """An unmapped tool declares the full (top-level) tokens and no type, so a
    typed policy holds it (fail toward oversight)."""
    _install_typed(monkeypatch)
    i = interaction_for("mystery_tool", {})
    assert i["AP"] == ["identity", "role"] and i["OP"] == ["session", "request"]
    assert "interaction_type" not in i


# ---- schema: optional interaction_type ------------------------------------

def _req(**extra):
    interaction = {"AP": ["identity"], "OP": ["session"], "context": {},
                   "expected_manifest_version": "1.1",
                   "expected_manifest_sha256": "a" * 64}
    interaction.update(extra)
    return {"target_url": "https://t.example/x", "interaction": interaction}


def test_schema_accepts_optional_interaction_type():
    norm, ref = validate_request(_req(interaction_type="read"))
    assert ref is None
    assert norm["interaction_type"] == "read"


def test_schema_absent_interaction_type_backward_compat():
    norm, ref = validate_request(_req())
    assert ref is None and "interaction_type" not in norm


def test_schema_non_string_interaction_type_rejected():
    norm, ref = validate_request(_req(interaction_type=7))
    assert norm is None and ref == REF_SCHEMA_TYPE_MISMATCH
