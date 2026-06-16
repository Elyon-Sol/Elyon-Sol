"""
Cert tooling for the Elyon-Sol TLS deployment (C2 / VL-082).

Generates a private dev CA and per-service leaf certificates (gate / target / publisher) using
the `cryptography` library only - no openssl binary dependency, so it runs anywhere the gate's
pinned crypto stack runs. The certs let the three C1 services serve under real TLS
(uvicorn --ssl-certfile/--ssl-keyfile) and let the gate/target clients verify their peers via the
transport.py ELYON_TLS_CA_BUNDLE hook.

For a REAL deployment the operator either (a) regenerates leaves with real hostnames under this
private CA (a closed network), or (b) uses a real / Let's Encrypt CA (a public network), in which
case clients trust the system store and ELYON_TLS_CA_BUNDLE is unset. See trust_bootstrap.md.

The generated private keys are out-of-band material - deploy/tls/certs/ is git-ignored.

Run:  python deploy/tls/gen_certs.py            # writes deploy/tls/certs/
      python deploy/tls/gen_certs.py host1 host2 ...   # extra SANs for all leaves
"""

import datetime
import ipaddress
import os
import sys

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

VALIDITY_DAYS = 825  # the CA/Browser-forum leaf cap; fine for a dev CA too.
# elyon-authz is the ext-authz admissibility sidecar (VL-104). Its leaf SAN is its
# compose DNS name, so Envoy (upstream TLS context) and a direct HTTPS caller both
# verify it under this CA - parity with the gate/target/publisher leaves (VL-105).
SERVICES = ("gate", "target", "publisher", "elyon-authz")


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _san_general_name(value):
    try:
        return x509.IPAddress(ipaddress.ip_address(value))
    except ValueError:
        return x509.DNSName(value)


def gen_ca(common_name="Elyon-Sol Dev CA"):
    """A self-signed CA (EC P-256). Not for public trust - a private CA for a closed network."""
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_now() - datetime.timedelta(minutes=5))
        .not_valid_after(_now() + datetime.timedelta(days=VALIDITY_DAYS * 4))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=False, key_encipherment=False,
                data_encipherment=False, key_agreement=False, key_cert_sign=True,
                crl_sign=True, encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False
        )
        .sign(key, hashes.SHA256())
    )
    return key, cert


def gen_leaf(ca_key, ca_cert, common_name, sans):
    """A leaf cert for `common_name` with `sans` (DNS names / IPs), signed by the CA. Usable for
    both server and client auth (mutual TLS)."""
    key = ec.generate_private_key(ec.SECP256R1())
    san_ext = x509.SubjectAlternativeName([_san_general_name(s) for s in sans])
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)]))
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_now() - datetime.timedelta(minutes=5))
        .not_valid_after(_now() + datetime.timedelta(days=VALIDITY_DAYS))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(san_ext, critical=False)
        .add_extension(
            x509.ExtendedKeyUsage(
                [ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]
            ),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    return key, cert


def key_pem(key):
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def cert_pem(cert):
    return cert.public_bytes(serialization.Encoding.PEM)


def write_deployment_certs(out_dir, extra_sans=()):
    """Write ca.crt + per-service {svc}.crt/{svc}.key. Each service SAN covers its compose
    service name, localhost, 127.0.0.1, plus any extra_sans (real hostnames)."""
    os.makedirs(out_dir, exist_ok=True)
    ca_key, ca_cert = gen_ca()
    with open(os.path.join(out_dir, "ca.crt"), "wb") as f:
        f.write(cert_pem(ca_cert))
    for svc in SERVICES:
        sans = [svc, "localhost", "127.0.0.1", *extra_sans]
        key, cert = gen_leaf(ca_key, ca_cert, svc, sans)
        with open(os.path.join(out_dir, svc + ".crt"), "wb") as f:
            f.write(cert_pem(cert))
        with open(os.path.join(out_dir, svc + ".key"), "wb") as f:
            f.write(key_pem(key))
    return out_dir


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
    extra = tuple(sys.argv[1:])
    write_deployment_certs(out, extra_sans=extra)
    print("wrote certs to", out)
    print("  ca.crt + {gate,target,publisher,elyon-authz}.{crt,key}")
    if extra:
        print("  extra SANs:", ", ".join(extra))
    print("  (private keys are out-of-band; deploy/tls/certs/ is git-ignored)")


if __name__ == "__main__":
    main()
