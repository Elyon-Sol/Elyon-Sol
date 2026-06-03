"""Pytest session fixtures for Elyon-Sol.

VL-047 mandatory signing cutover: pep.py's default ELIGIBLE forward now signs
the envelope, so every test that drives the gate's ELIGIBLE path needs a
signing key configured. The autouse `gate_signing` fixture installs an
ephemeral Ed25519 keypair into pep._get_signing_key for the duration of each
test - modeling a deployed gate that HAS a key. The private key lives only in
the test process and is never written to disk (the project-wide key custody
rule; artifact 09 / artifact 05 "Key model").

Tests that need the gate's public key (to construct a key-pinning verifying
target) request the `gate_signing` fixture by name; it returns
{"public_key", "key_id", "private_key"}.

A test marked @pytest.mark.no_gate_key opts OUT: the fixture forces
pep._get_signing_key -> None so the no-key fail-closed path
(REF_PEP_FAIL_CLOSED, never a downgrade to an unsigned forward) can be
exercised.
"""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


GATE_TEST_KEY_ID = "gate-test-ed25519-001"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "no_gate_key: run with pep._get_signing_key forced to None "
        "(the no-key fail-closed path).",
    )


@pytest.fixture(autouse=True)
def gate_signing(request, monkeypatch):
    import IMPLEMENTATION.pep as pep

    if "no_gate_key" in request.keywords:
        monkeypatch.setattr(pep, "_get_signing_key", lambda: None)
        yield None
        return

    priv = Ed25519PrivateKey.generate()
    monkeypatch.setattr(pep, "_get_signing_key", lambda: (priv, GATE_TEST_KEY_ID))
    yield {
        "public_key": priv.public_key(),
        "key_id": GATE_TEST_KEY_ID,
        "private_key": priv,
    }
