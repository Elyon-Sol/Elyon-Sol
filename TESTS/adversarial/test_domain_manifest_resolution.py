"""S5b - the compose-in contract: resolving the deployed domain manifest.

The load-bearing distinction is ABSENT vs MALFORMED. Conflating them is how
composing D would brick a flat deployment into refuse-all (absent treated as an
error) or silently bypass enforcement (malformed treated as "no policy").
"""
import json
import os
import tempfile

import pytest

from IMPLEMENTATION.domain_validity import (
    resolve_domain_manifest, assess, safe_domain_manifest,
    UNARMED_DOMAIN_MANIFEST, DOMAIN_MANIFEST_DEFAULT_PATH,
    DM_STATUS_ABSENT, DM_STATUS_LOADED, DM_STATUS_MALFORMED,
)


def _tmp(content, *, raw=False):
    p = os.path.join(tempfile.mkdtemp(), "dm.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content if raw else json.dumps(content))
    return p


# --- ABSENT: D was never deployed -> inert, NOT refuse-all -------------------

def test_absent_resolves_unarmed_not_error():
    m, status = resolve_domain_manifest(os.path.join(tempfile.mkdtemp(), "nope.json"))
    assert status == DM_STATUS_ABSENT
    assert m == UNARMED_DOMAIN_MANIFEST


def test_absent_manifest_passes_everything_through():
    """The anti-brick property: with no ruleset deployed, D must not refuse."""
    m, _ = resolve_domain_manifest(os.path.join(tempfile.mkdtemp(), "nope.json"))
    for ctx in ({}, {"domain": "anything", "context": {"whatever": False}},
                {"context": {}}, {"domain": "healthcare_admin", "context": {}}):
        assert assess(ctx, m) == ("VALID", None, None)


# --- MALFORMED: deployed but broken -> fail closed ---------------------------

@pytest.mark.parametrize("bad", [
    ("{not json", True),
    ({"version": 1}, False),                                        # version not str
    ({"version": "1.0", "domains": "nope"}, False),                 # domains not dict
    ({"version": "1.0", "domains": {"d": {"predicates": "no"}}}, False),
    ({"version": "1.0", "domains": {"d": {"predicates": [], "requires_verdict": True}}}, False),
])
def test_malformed_resolves_none_for_fail_closed(bad):
    content, raw = bad
    m, status = resolve_domain_manifest(_tmp(content, raw=raw))
    assert status == DM_STATUS_MALFORMED
    assert m is None, "a broken ruleset must NOT degrade to 'no ruleset'"


def test_malformed_is_not_silently_unarmed():
    """The dangerous conflation: a broken config must never be read as inert."""
    m, status = resolve_domain_manifest(_tmp({"version": "1.0", "domains": "broken"}))
    assert (m, status) != (UNARMED_DOMAIN_MANIFEST, DM_STATUS_ABSENT)


# --- LOADED: a real ruleset is in force --------------------------------------

def test_armed_example_loads():
    m, status = resolve_domain_manifest("MANIFEST/domain_manifest.example.json")
    assert status == DM_STATUS_LOADED
    assert safe_domain_manifest(m) is not None
    assert m["domains"]


def test_tracked_default_is_wellformed_and_unarmed():
    """The tracked default must be inert so a checkout that never configured D
    behaves exactly as it did before D existed."""
    m, status = resolve_domain_manifest(DOMAIN_MANIFEST_DEFAULT_PATH)
    assert status == DM_STATUS_LOADED
    assert safe_domain_manifest(m) is not None
    assert not m.get("domains"), "the tracked default must declare no domains"
    assert assess({"domain": "x", "context": {}}, m) == ("VALID", None, None)


def test_default_path_used_when_none_given():
    m, status = resolve_domain_manifest()
    assert status == DM_STATUS_LOADED and not m.get("domains")


# --- the unarmed constant itself ---------------------------------------------

def test_unarmed_constant_is_wellformed_and_inert():
    assert safe_domain_manifest(UNARMED_DOMAIN_MANIFEST) is not None
    assert assess({"domain": "d", "context": {}}, UNARMED_DOMAIN_MANIFEST) == ("VALID", None, None)
