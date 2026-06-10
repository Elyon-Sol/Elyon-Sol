"""
C2 TLS cert tooling tests (docs/restructure/21_real_tls_and_trust_bootstrap_spec.md, VL-082).

C2's sandbox-green referent: the generated cert MATERIAL is correct and actually establishes a
VERIFIED TLS session. The chain validates (CA self-signed + CA:TRUE; leaf CA-signed, in-window,
expected SAN), and a REAL TLS handshake - driven over an in-memory BIO, no sockets/processes -
between a server holding the leaf and a client trusting the CA SUCCEEDS and verifies the peer,
while a client trusting a DIFFERENT CA is REFUSED (fail-closed). A real two-host TLS run and a
real / Let's Encrypt CA are the author's (locus AUTHOR).
"""

import datetime
import os
import ssl
import tempfile

from cryptography.hazmat.primitives.asymmetric import ec
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
    """Run a real TLS handshake over MemoryBIO. Returns the verified peer cert (client side).
    Raises ssl.SSLCertVerificationError if the client cannot verify the server."""
    with tempfile.TemporaryDirectory() as tmp:
        cert_f = _write(tmp, "s.crt", server_cert_pem)
        key_f = _write(tmp, "s.key", server_key_pem)
        server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_ctx.load_cert_chain(cert_f, key_f)
        client_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_ctx.load_verify_locations(cadata=client_trust_pem.decode("ascii"))
        client_ctx.check_hostname = True
        client_ctx.verify_mode = ssl.CERT_REQUIRED
        # Strict X.509 (matches OpenSSL 3.x on a real client, e.g. Python 3.13 on
        # Windows): requires the CA's Subject Key Identifier + the leaf's Authority
        # Key Identifier. The live cross-host run surfaced their absence (Lesson 12).
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            client_ctx.verify_flags |= ssl.VERIFY_X509_STRICT

        s_in, s_out = ssl.MemoryBIO(), ssl.MemoryBIO()
        c_in, c_out = ssl.MemoryBIO(), ssl.MemoryBIO()
        sobj = server_ctx.wrap_bio(s_in, s_out, server_side=True)
        cobj = client_ctx.wrap_bio(c_in, c_out, server_hostname=server_hostname)
        _drive_handshake(cobj, c_in, c_out, sobj, s_in, s_out)
        return cobj.getpeercert()


def test_ca_is_self_signed_and_a_ca():
    ca_key, ca_cert = g.gen_ca()
    assert ca_cert.subject == ca_cert.issuer
    bc = ca_cert.extensions.get_extension_for_class(x509.BasicConstraints).value
    assert bc.ca is True
    # self-signed: the CA verifies its own signature
    ca_cert.public_key().verify(
        ca_cert.signature, ca_cert.tbs_certificate_bytes,
        ec.ECDSA(ca_cert.signature_hash_algorithm),
    )


def test_leaf_is_ca_signed_in_window_with_san():
    ca_key, ca_cert = g.gen_ca()
    _key, cert = g.gen_leaf(ca_key, ca_cert, "target", ["target", "127.0.0.1"])
    # signed by the CA (raises if not)
    ca_cert.public_key().verify(
        cert.signature, cert.tbs_certificate_bytes,
        ec.ECDSA(cert.signature_hash_algorithm),
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    assert cert.not_valid_before_utc <= now < cert.not_valid_after_utc
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert "target" in san.get_values_for_type(x509.DNSName)
    assert not cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    # SKI + AKI are required by strict OpenSSL 3.x chain building (VL-087):
    cert.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
    cert.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier)


def test_real_tls_handshake_verifies_with_trusted_ca():
    ca_key, ca_cert = g.gen_ca()
    leaf_key, leaf_cert = g.gen_leaf(ca_key, ca_cert, "target", ["target", "localhost"])
    peer = _handshake(
        g.cert_pem(leaf_cert), g.key_pem(leaf_key), g.cert_pem(ca_cert),
        server_hostname="target",
    )
    # A verified peer cert is returned only on a successful, verified handshake.
    assert peer is not None and peer != {}


def test_real_tls_handshake_refused_with_wrong_ca():
    ca_key, ca_cert = g.gen_ca()
    leaf_key, leaf_cert = g.gen_leaf(ca_key, ca_cert, "target", ["target", "localhost"])
    other_ca_key, other_ca_cert = g.gen_ca("Some Other CA")  # client trusts the WRONG CA
    import pytest
    with pytest.raises(ssl.SSLCertVerificationError):
        _handshake(
            g.cert_pem(leaf_cert), g.key_pem(leaf_key), g.cert_pem(other_ca_cert),
            server_hostname="target",
        )


def test_write_deployment_certs_emits_all_files():
    with tempfile.TemporaryDirectory() as tmp:
        g.write_deployment_certs(tmp, extra_sans=("gate.example.com",))
        for f in ("ca.crt", "gate.crt", "gate.key", "target.crt", "target.key",
                  "publisher.crt", "publisher.key"):
            assert os.path.isfile(os.path.join(tmp, f)), f


def test_tls_overlay_wires_ssl_and_ca_bundle():
    # Dependency-free structural check (no pyyaml in CI deps): the TLS overlay
    # serves under uvicorn --ssl-* and points clients at the CA bundle over https.
    text = open("deploy/docker-compose.tls.yml").read()
    assert "--ssl-certfile" in text and "--ssl-keyfile" in text
    assert "ELYON_TLS_CA_BUNDLE: /certs/ca.crt" in text
    assert "https://target:9000/target" in text
    assert "https://publisher:9100/published_hashes.json" in text
    for svc in ("/certs/gate.crt", "/certs/target.crt", "/certs/publisher.crt"):
        assert svc in text, svc
