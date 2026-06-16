"""
TLS cert tooling tests for the ext-authz sidecar (VL-105).

Sandbox-green referent for serving `elyon-authz` under TLS (the C2 posture, parity
with TESTS/deploy/test_tls_certs.py): the generated `elyon-authz` leaf material is
correct and actually establishes a VERIFIED TLS session. A REAL TLS handshake -
driven over an in-memory BIO, no sockets/processes, so it is hermetic/CI-safe -
between a server holding the elyon-authz leaf and a client trusting the dev CA
SUCCEEDS and verifies the peer, while a client trusting a DIFFERENT CA is REFUSED
(fail-closed). A real two-host TLS run is the author's (deploy/elyon-authz/VM_TLS_TEST.md);
the stronger in-sandbox demonstration (the sidecar served over a real loopback TLS
socket, answering ALLOW/DENY over HTTPS) is EVIDENCE/proofs/authz_sidecar_tls_001_runner.py.
"""

import os
import ssl
import tempfile

import pytest

from cryptography import x509

import deploy.tls.gen_certs as g


def _write(tmp, name, data):
    p = os.path.join(tmp, name)
    with open(p, "wb") as f:
        f.write(data)
    return p


def _drive_handshake(cobj, c_in, c_out, sobj, s_in, s_out):
    client_done = server_done = False
    for _ in range(50):
        if not client_done:
            try:
                cobj.do_handshake()
                client_done = True
            except ssl.SSLWantReadError:
                pass
        buf = c_out.read()
        if buf:
            s_in.write(buf)
        if not server_done:
            try:
                sobj.do_handshake()
                server_done = True
            except ssl.SSLWantReadError:
                pass
        buf = s_out.read()
        if buf:
            c_in.write(buf)
        if client_done and server_done:
            return
    raise RuntimeError("handshake did not complete")


def _handshake(server_cert_pem, server_key_pem, client_trust_pem, server_hostname):
    """A real strict TLS handshake over MemoryBIO (no sockets). Returns the verified
    peer cert; raises ssl.SSLCertVerificationError if the client cannot verify the
    server. Strict X.509 (VERIFY_X509_STRICT) matches OpenSSL 3.x on a real client."""
    with tempfile.TemporaryDirectory() as tmp:
        cert_f = _write(tmp, "s.crt", server_cert_pem)
        key_f = _write(tmp, "s.key", server_key_pem)
        server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_ctx.load_cert_chain(cert_f, key_f)
        client_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_ctx.load_verify_locations(cadata=client_trust_pem.decode("ascii"))
        client_ctx.check_hostname = True
        client_ctx.verify_mode = ssl.CERT_REQUIRED
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            client_ctx.verify_flags |= ssl.VERIFY_X509_STRICT
        s_in, s_out = ssl.MemoryBIO(), ssl.MemoryBIO()
        c_in, c_out = ssl.MemoryBIO(), ssl.MemoryBIO()
        sobj = server_ctx.wrap_bio(s_in, s_out, server_side=True)
        cobj = client_ctx.wrap_bio(c_in, c_out, server_hostname=server_hostname)
        _drive_handshake(cobj, c_in, c_out, sobj, s_in, s_out)
        return cobj.getpeercert()


def test_elyon_authz_leaf_verifies_with_trusted_ca():
    ca_key, ca_cert = g.gen_ca()
    leaf_key, leaf_cert = g.gen_leaf(
        ca_key, ca_cert, "elyon-authz", ["elyon-authz", "localhost"]
    )
    peer = _handshake(
        g.cert_pem(leaf_cert), g.key_pem(leaf_key), g.cert_pem(ca_cert),
        server_hostname="elyon-authz",
    )
    assert peer is not None and peer != {}


def test_elyon_authz_leaf_refused_with_wrong_ca():
    ca_key, ca_cert = g.gen_ca()
    leaf_key, leaf_cert = g.gen_leaf(
        ca_key, ca_cert, "elyon-authz", ["elyon-authz", "localhost"]
    )
    other_ca_key, other_ca_cert = g.gen_ca("Some Other CA")
    with pytest.raises(ssl.SSLCertVerificationError):
        _handshake(
            g.cert_pem(leaf_cert), g.key_pem(leaf_key), g.cert_pem(other_ca_cert),
            server_hostname="elyon-authz",
        )


def test_write_deployment_certs_emits_elyon_authz_leaf():
    with tempfile.TemporaryDirectory() as tmp:
        g.write_deployment_certs(tmp, extra_sans=("authz.example.com",))
        for f in ("ca.crt", "elyon-authz.crt", "elyon-authz.key"):
            assert os.path.isfile(os.path.join(tmp, f)), f
        cert = x509.load_pem_x509_certificate(
            open(os.path.join(tmp, "elyon-authz.crt"), "rb").read()
        )
        dns = cert.extensions.get_extension_for_class(
            x509.SubjectAlternativeName
        ).value.get_values_for_type(x509.DNSName)
        assert "elyon-authz" in dns and "authz.example.com" in dns


def test_authz_tls_overlay_wires_ssl():
    # Dependency-free structural check (no pyyaml in CI deps): the sidecar TLS
    # overlay serves elyon-authz under uvicorn --ssl-* with its leaf + the CA mount.
    text = open("deploy/docker-compose.authz.tls.yml").read()
    assert "--ssl-certfile" in text and "--ssl-keyfile" in text
    assert "/certs/elyon-authz.crt" in text and "/certs/elyon-authz.key" in text
    assert "./tls/certs:/certs:ro" in text
