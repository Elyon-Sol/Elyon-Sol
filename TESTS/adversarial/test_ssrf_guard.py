"""L1 SSRF guard — the gate must not http-forward to internal/loopback/metadata."""
import pytest
from IMPLEMENTATION.pep import _target_url_allowed


@pytest.fixture(autouse=True)
def _guard_on(monkeypatch):
    monkeypatch.delenv("ELYON_ALLOW_PRIVATE_TARGETS", raising=False)
    monkeypatch.delenv("ELYON_TARGET_URL_ALLOWLIST", raising=False)


@pytest.mark.parametrize("url", [
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",  # cloud metadata
    "http://127.0.0.1:8080/admin",
    "http://localhost/x",
    "http://10.0.0.5/x",
    "http://192.168.1.1/x",
    "http://172.16.0.9/x",
    "http://[::1]/x",
    "https://0.0.0.0/x",
])
def test_internal_http_blocked(url):
    assert _target_url_allowed(url) is False


@pytest.mark.parametrize("url", ["https://8.8.8.8/x", "http://1.1.1.1/path"])
def test_public_http_allowed(url):
    assert _target_url_allowed(url) is True


@pytest.mark.parametrize("url", ["mcp://elyon-sol/tool-server", "urn:x:y"])
def test_non_http_schemes_pass_through(url):
    # Out of this guard's scope: not an http(s) forward, so not an SSRF-to-internal
    # vector (requests rejects the scheme downstream anyway).
    assert _target_url_allowed(url) is True


def test_allowlist_mode(monkeypatch):
    monkeypatch.setenv("ELYON_TARGET_URL_ALLOWLIST", "target.elyon-sol.io")
    assert _target_url_allowed("https://target.elyon-sol.io:9443/target") is True
    assert _target_url_allowed("https://evil.example/x") is False
    assert _target_url_allowed("http://127.0.0.1/x") is False


def test_dev_optout(monkeypatch):
    monkeypatch.setenv("ELYON_ALLOW_PRIVATE_TARGETS", "1")
    assert _target_url_allowed("http://127.0.0.1/x") is True
