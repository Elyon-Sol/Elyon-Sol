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


def test_forward_does_not_follow_redirects():
    """The guard vets only the first URL, so the forward must not follow a 3xx:
    a vetted host answering 307 -> an internal address would otherwise receive
    the signed envelope. Two loopback servers: the first redirects to the second;
    post_to_target returns the 307 and the second is never contacted."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from IMPLEMENTATION.transport import post_to_target

    hits = []

    class Internal(BaseHTTPRequestHandler):
        def do_POST(self):
            hits.append(self.headers.get("X-Elyon-Sol-Envelope"))
            self.send_response(200)
            self.end_headers()

        def log_message(self, *a):
            pass

    internal = HTTPServer(("127.0.0.1", 0), Internal)

    class Redirector(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(307)
            self.send_header("Location",
                             f"http://127.0.0.1:{internal.server_port}/internal")
            self.end_headers()

        def log_message(self, *a):
            pass

    outer = HTTPServer(("127.0.0.1", 0), Redirector)
    for s in (internal, outer):
        threading.Thread(target=s.serve_forever, daemon=True).start()
    try:
        r = post_to_target(f"http://127.0.0.1:{outer.server_port}/hook", {"x": 1},
                           {"X-Elyon-Sol-Envelope": "{}"}, timeout=5)
        assert r.status_code == 307
        assert hits == []
    finally:
        outer.shutdown()
        internal.shutdown()


def test_forward_failure_does_not_echo_connection_detail(monkeypatch):
    """A failed forward refuses with the exception CLASS only: the message
    (host/port, refused vs. timed out) would make the gate a reachability
    oracle for internal scanning."""
    import requests
    from fastapi.testclient import TestClient
    import IMPLEMENTATION.pep as pep
    from IMPLEMENTATION.mcp_server import interaction_for

    def refused(*a, **k):
        raise requests.ConnectionError("HTTPConnectionPool(host='10.0.0.7', port=6379)")

    monkeypatch.setattr("IMPLEMENTATION.pep.requests.post", refused)
    r = TestClient(pep.app).post(
        "/governed-call",
        json={"target_url": "https://8.8.8.8/x",
              "interaction": interaction_for("transfer_funds", {"amount": 1})},
    )
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert detail["refusal_reason_code"] == "REF_PEP_FAIL_CLOSED"
    assert detail["error"] == "ConnectionError"
    assert "6379" not in r.text and "10.0.0.7" not in r.text
