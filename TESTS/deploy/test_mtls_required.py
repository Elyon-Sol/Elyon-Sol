"""
Feature 2 (non-bypassable enforcement), the load-bearing proof (design 2.3):
the target refuses any client that is not the gate AT THE TLS LAYER, before any
app logic. This elevates A1 from "the app refuses bare calls" to "the network
refuses to carry a bypassing call at all".

Hermetic: a real TLS handshake over MemoryBIO (no sockets/processes), reusing
deploy.tls.gen_certs (the leaves already carry SERVER_AUTH + CLIENT_AUTH EKU).
The real-socket version is EVIDENCE/proofs/nonbypass_direct_call_refused_runner.py.

The star test is the bypass refusal: a connection WITHOUT the gate client cert
fails the handshake when the target requires client auth (mTLS). The contrast
test shows that without CERT_REQUIRED (one-way TLS, today's default) the same
bare connection WOULD be accepted - i.e. mTLS is exactly what closes the gap.
"""

import ssl
import tempfile
import os

import pytest

import deploy.tls.gen_certs as g


CA_NAME = "Elyon-Sol Dev CA"
TARGET_HOST = "target.elyon.local"
GATE_CN = "gate.elyon.local"


def _write(tmp, name, data):
    p = os.path.join(tmp, name)
    with open(p, "wb") as f:
        f.write(data)
    return p


def _drive(cobj, c_in, c_out, sobj, s_in, s_out):
    """Pump a TLS handshake between two MemoryBIO endpoints. Raises whatever SSL
    error either side raises (e.g. the server rejecting a missing client cert)."""
    client_done = server_done = False
    for _ in range(50):
        if not client_done:
            try:
                cobj.do_handshake(); client_done = True
            except ssl.SSLWantReadError:
                pass
        buf = c_out.read()
        if buf:
            s_in.write(buf)
        if not server_done:
            try:
                sobj.do_handshake(); server_done = True
            except ssl.SSLWantReadError:
                pass
        buf = s_out.read()
        if buf:
            c_in.write(buf)
        if client_done and server_done:
            return
    raise RuntimeError("handshake did not complete")


def _mtls_handshake(target_cert, target_key, ca_pem, *,
                    client_cert=None, client_key=None, require_client=True):
    """Drive a handshake: target (server) optionally requiring a client cert,
    a client optionally presenting one. Returns the client cert the SERVER
    observed (its proof of who connected). Raises on handshake failure."""
    with tempfile.TemporaryDirectory() as tmp:
        s_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        s_ctx.load_cert_chain(_write(tmp, "t.crt", target_cert),
                              _write(tmp, "t.key", target_key))
        if require_client:
            # the gate-only door: verify + REQUIRE a CA-signed client cert
            s_ctx.verify_mode = ssl.CERT_REQUIRED
            s_ctx.load_verify_locations(cadata=ca_pem.decode("ascii"))

        c_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        c_ctx.load_verify_locations(cadata=ca_pem.decode("ascii"))
        c_ctx.check_hostname = True
        c_ctx.verify_mode = ssl.CERT_REQUIRED
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            c_ctx.verify_flags |= ssl.VERIFY_X509_STRICT
        if client_cert is not None:
            c_ctx.load_cert_chain(_write(tmp, "c.crt", client_cert),
                                  _write(tmp, "c.key", client_key))

        s_in, s_out = ssl.MemoryBIO(), ssl.MemoryBIO()
        c_in, c_out = ssl.MemoryBIO(), ssl.MemoryBIO()
        sobj = s_ctx.wrap_bio(s_in, s_out, server_side=True)
        cobj = c_ctx.wrap_bio(c_in, c_out, server_hostname=TARGET_HOST)
        _drive(cobj, c_in, c_out, sobj, s_in, s_out)
        return sobj.getpeercert()


@pytest.fixture(scope="module")
def pki():
    ca_key, ca_cert = g.gen_ca(CA_NAME)
    ca_pem = g.cert_pem(ca_cert)
    tk, tc = g.gen_leaf(ca_key, ca_cert, TARGET_HOST, [TARGET_HOST])
    gk, gc = g.gen_leaf(ca_key, ca_cert, GATE_CN, [GATE_CN])
    # a second, untrusted CA (a stranger) and a leaf it signed
    rogue_key, rogue_cert = g.gen_ca("Rogue CA")
    rk, rc = g.gen_leaf(rogue_key, rogue_cert, GATE_CN, [GATE_CN])
    return {
        "ca_pem": ca_pem,
        "target": (g.cert_pem(tc), g.key_pem(tk)),
        "gate": (g.cert_pem(gc), g.key_pem(gk)),
        "rogue": (g.cert_pem(rc), g.key_pem(rk)),
    }


def test_gate_with_client_cert_is_honored(pki):
    """A call THROUGH the gate (presenting the CA-signed client cert) completes
    the mTLS handshake, and the target sees the gate's identity."""
    tc, tk = pki["target"]; gc, gk = pki["gate"]
    peer = _mtls_handshake(tc, tk, pki["ca_pem"], client_cert=gc, client_key=gk)
    assert peer is not None  # a verified client cert was presented
    subject = dict(x[0] for x in peer["subject"])
    assert subject.get("commonName") == GATE_CN


def test_direct_call_without_client_cert_is_refused_REVERT_CATCHER(pki):
    """star (design 2.3): a direct connection to the target WITHOUT the gate
    client cert is rejected at the TLS handshake, before any app logic.
    Reverting the target to one-way TLS (no CERT_REQUIRED) would accept it -
    the bypass the contrast test below demonstrates."""
    tc, tk = pki["target"]
    with pytest.raises(ssl.SSLError):
        _mtls_handshake(tc, tk, pki["ca_pem"], client_cert=None, require_client=True)


def test_one_way_tls_would_accept_the_bare_call_contrast(pki):
    """Contrast: with the target in one-way TLS (require_client=False, today's
    default per the TLS dossier 9.5), the same bare client IS accepted at the
    transport - which is why mTLS is the layer that closes A1, not TLS alone."""
    tc, tk = pki["target"]
    peer = _mtls_handshake(tc, tk, pki["ca_pem"], client_cert=None, require_client=False)
    assert peer in (None, {})  # accepted; the server simply saw no client cert


def test_client_cert_from_untrusted_ca_is_refused(pki):
    """A client presenting a cert NOT signed by the trusted CA (a forged/rogue
    gate) is rejected at the handshake."""
    tc, tk = pki["target"]; rc, rk = pki["rogue"]
    with pytest.raises(ssl.SSLError):
        _mtls_handshake(tc, tk, pki["ca_pem"], client_cert=rc, client_key=rk)
