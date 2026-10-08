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
    # The allowlisted origin is admitted; anything else, including loopback, is not.
    monkeypatch.setenv("ELYON_TARGET_URL_ALLOWLIST", "https://target.elyon-sol.io:9443")
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


# ---------------------------------------------------------------------------
# DNS rebinding between the guard's resolution and the forward's (VL-154 open
# item). The guard resolves a name once and vets the answer; the forward must
# connect to THAT address, never resolve the name a second time.
# ---------------------------------------------------------------------------

def _fake_resolver(monkeypatch, answers):
    """Patch socket.getaddrinfo (shared by the guard and by urllib3's connect).
    `answers[host]` is the sequence of addresses served to successive lookups
    of that host (the last one repeats; None = NXDOMAIN). Other hosts use the
    real resolver. Returns the list of patched-host lookups, in order."""
    import socket
    real = socket.getaddrinfo
    lookups = []
    counts = {}

    def fake(host, port, *args, **kwargs):
        if host not in answers:
            return real(host, port, *args, **kwargs)
        n = counts.get(host, 0)
        counts[host] = n + 1
        lookups.append(host)
        seq = answers[host]
        addr = seq[min(n, len(seq) - 1)]
        if addr is None:
            raise socket.gaierror(-2, "Name or service not known")
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (addr, port))]

    monkeypatch.setattr(socket, "getaddrinfo", fake)
    return lookups


def _loopback_server(ssl_context=None):
    """An HTTP(S) server on 127.0.0.1 that records each request's Host header."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    seen = []

    class Target(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            seen.append(self.headers.get("Host"))
            self.send_response(200)
            self.end_headers()

        def log_message(self, *a):
            pass

    server = HTTPServer(("127.0.0.1", 0), Target)
    if ssl_context is not None:
        server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, seen


def test_forward_connects_to_the_pinned_address_not_a_fresh_lookup(monkeypatch):
    """post_to_target(pinned_ip=...) connects to the pinned address and never
    resolves the URL's name: here the name does not resolve at all any more
    (what a rebinding resolver's second answer amounts to), yet the forward
    reaches the pinned loopback server, with the Host header still naming the
    original host and port."""
    from IMPLEMENTATION.transport import post_to_target

    lookups = _fake_resolver(monkeypatch, {"rebind.test": [None]})
    server, seen = _loopback_server()
    try:
        port = server.server_port
        r = post_to_target(f"http://rebind.test:{port}/hook", {"x": 1},
                           {"X-Elyon-Sol-Envelope": "{}"}, timeout=5,
                           pinned_ip="127.0.0.1")
        assert r.status_code == 200
        assert seen == [f"rebind.test:{port}"]
        assert lookups == []
    finally:
        server.shutdown()


def _tls_server_for(name):
    """A loopback HTTPS server presenting a leaf for `name`; returns
    (server, seen, ca_bundle_path, tmpdir)."""
    import os
    import ssl
    import tempfile
    import deploy.tls.gen_certs as g

    ca_key, ca_cert = g.gen_ca()
    leaf_key, leaf_cert = g.gen_leaf(ca_key, ca_cert, name, [name])
    tmp = tempfile.mkdtemp()
    paths = {}
    for fname, data in (("ca.crt", g.cert_pem(ca_cert)),
                        ("leaf.crt", g.cert_pem(leaf_cert)),
                        ("leaf.key", g.key_pem(leaf_key))):
        paths[fname] = os.path.join(tmp, fname)
        with open(paths[fname], "wb") as f:
            f.write(data)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(paths["leaf.crt"], paths["leaf.key"])
    server, seen = _loopback_server(ctx)
    return server, seen, paths["ca.crt"]


def test_pinned_https_forward_keeps_sni_and_certificate_verification(monkeypatch):
    """Pinning the address must not weaken TLS: the connection goes to the
    pinned IP, but SNI and the certificate check still use the URL's name. A
    leaf issued for that name is accepted; one issued for another name is
    refused even though the pinned address is reachable."""
    import requests
    from IMPLEMENTATION.transport import post_to_target

    _fake_resolver(monkeypatch, {"rebind.test": [None]})

    server, seen, ca = _tls_server_for("rebind.test")
    try:
        port = server.server_port
        r = post_to_target(f"https://rebind.test:{port}/hook", {"x": 1},
                           {"X-Elyon-Sol-Envelope": "{}"}, timeout=5,
                           verify=ca, pinned_ip="127.0.0.1")
        assert r.status_code == 200
        assert seen == [f"rebind.test:{port}"]
    finally:
        server.shutdown()

    server, seen, ca = _tls_server_for("other.test")
    try:
        port = server.server_port
        with pytest.raises(requests.exceptions.SSLError):
            post_to_target(f"https://rebind.test:{port}/hook", {"x": 1},
                           {"X-Elyon-Sol-Envelope": "{}"}, timeout=5,
                           verify=ca, pinned_ip="127.0.0.1")
        assert seen == []
    finally:
        server.shutdown()


def test_governed_call_forwards_to_the_address_the_guard_vetted(monkeypatch):
    """The gate resolves the target name exactly once - in the guard - and the
    forward is handed that address. The resolver answers a public address to
    the first lookup and 127.0.0.1 to every later one (DNS rebinding); the
    forward must still be pinned to the vetted public address."""
    from fastapi.testclient import TestClient
    import IMPLEMENTATION.pep as pep
    from IMPLEMENTATION.mcp_server import interaction_for

    lookups = _fake_resolver(monkeypatch,
                             {"rebind.test": ["93.184.216.34", "127.0.0.1"]})
    captured = {}

    class _Resp:
        status_code = 200

    def fake_post(url, body, headers, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return _Resp()

    monkeypatch.setattr("IMPLEMENTATION.pep.post_to_target", fake_post)
    r = TestClient(pep.app).post(
        "/governed-call",
        json={"target_url": "https://rebind.test/x",
              "interaction": interaction_for("transfer_funds", {"amount": 1})},
    )
    assert r.status_code == 200
    assert r.json()["decision"] == "ELIGIBLE"
    assert captured["url"] == "https://rebind.test/x"
    assert captured["kwargs"].get("pinned_ip") == "93.184.216.34"
    assert lookups == ["rebind.test"]


def test_ip_literal_and_optout_targets_are_not_pinned(monkeypatch):
    """No pin when the guard did not resolve a name: an IP literal (nothing to
    rebind) and the dev opt-out (no resolution at all) leave the forward
    unchanged."""
    from IMPLEMENTATION.pep import _resolve_target

    assert _resolve_target("https://8.8.8.8/x") == (True, None)
    assert _resolve_target("http://127.0.0.1/x") == (False, None)
    monkeypatch.setenv("ELYON_ALLOW_PRIVATE_TARGETS", "1")
    assert _resolve_target("http://127.0.0.1/x") == (True, None)


# ---------------------------------------------------------------------------
# Guard gaps (VL-154 open items): the shared address space 100.64.0.0/10 passed
# the address predicate, and the allowlist matched the hostname alone.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://100.64.0.1/x",            # RFC 6598 shared address space (CGNAT)
    "http://100.127.255.254/x",
    "http://[::ffff:100.64.0.1]/x",   # the same, IPv4-mapped
    "http://[2002:7f00:1::]/x",       # 6to4 wrapping 127.0.0.1
    "http://[64:ff9b::7f00:1]/x",     # NAT64 well-known prefix
    "http://192.0.0.8/x",             # IETF protocol assignments
    "http://198.18.0.1/x",            # benchmarking
    "http://240.0.0.1/x",             # reserved
    "http://224.0.0.1/x",             # multicast
])
def test_non_global_space_blocked(url):
    assert _target_url_allowed(url) is False


@pytest.mark.parametrize("url", ["https://8.8.8.8/x", "http://[2001:4860:4860::8888]/x"])
def test_global_space_still_allowed(url):
    assert _target_url_allowed(url) is True


def test_allowlist_bare_host_admits_default_port_only(monkeypatch):
    """A bare hostname entry admits that host on the scheme's default port and
    nothing else: an allowlisted host must not expose every other service on
    the same box (redis on 6379, an admin port) to a signed forward."""
    monkeypatch.setenv("ELYON_TARGET_URL_ALLOWLIST", "target.example")
    assert _target_url_allowed("https://target.example/target") is True
    assert _target_url_allowed("https://target.example:443/target") is True
    assert _target_url_allowed("http://target.example/target") is True
    assert _target_url_allowed("http://target.example:6379/") is False
    assert _target_url_allowed("https://target.example:9443/target") is False
    assert _target_url_allowed("http://TARGET.example/target") is True  # case-insensitive host


def test_allowlist_host_port_entry_pins_the_port(monkeypatch):
    monkeypatch.setenv("ELYON_TARGET_URL_ALLOWLIST", "target:9000")
    assert _target_url_allowed("http://target:9000/target") is True
    assert _target_url_allowed("https://target:9000/target") is True   # either scheme, that port
    assert _target_url_allowed("http://target:9001/target") is False
    assert _target_url_allowed("http://target/target") is False         # default port not admitted


def test_allowlist_origin_entry_pins_scheme_and_port(monkeypatch):
    monkeypatch.setenv("ELYON_TARGET_URL_ALLOWLIST", "https://target:9000, https://other.example")
    assert _target_url_allowed("https://target:9000/target") is True
    assert _target_url_allowed("http://target:9000/target") is False    # scheme pinned
    assert _target_url_allowed("https://target:9001/target") is False   # port pinned
    assert _target_url_allowed("https://other.example/x") is True       # origin default port
    assert _target_url_allowed("https://other.example:8443/x") is False


def test_allowlist_malformed_port_in_url_refused(monkeypatch):
    monkeypatch.setenv("ELYON_TARGET_URL_ALLOWLIST", "target:9000")
    assert _target_url_allowed("http://target:notaport/target") is False
