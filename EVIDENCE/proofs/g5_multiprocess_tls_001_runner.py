"""
Multi-process + real-TLS chain runner (VL-063; artifact 12 steps 2-3, in-env).

The in-env realization of the G5 build's "two-node" step: the gate, the reference
enforcing target, and the published-record publisher run as THREE SEPARATE OS
PROCESSES on one host, talking over REAL TLS sockets with a local test CA - no
in-process shortcut, no monkeypatch, no capture/redeliver on the honor path. It
is the no-docker, single-host rung of docs/restructure/12_g5_transport_design.md
(docker-compose and two-real-VM promotion remain deploy-target artifacts; the
sandbox has no docker and is one host). True cross-host networking + an EXTERNAL
attacker is finish line (B), author-arranged; per GR-3 this runner CHARACTERIZES,
it does not certify.

Topology (all on 127.0.0.1, each its own uvicorn process, each over HTTPS):
  publisher (IMPLEMENTATION.publisher:app)         serves the published record
  target    (IMPLEMENTATION.reference_target:app)  fetches the record + verifies
  gate      (IMPLEMENTATION.pep:app)               signs + forwards on ELIGIBLE

Real TLS hops exercised (all CA-verified against the local test CA):
  runner -> gate     (drive a call)
  gate   -> target   (the ELIGIBLE forward; the transport seam resolves verify
                      from ELYON_TLS_CA_BUNDLE - VL-058/060)
  target -> publisher(the published-record fetch over TLS)
  runner -> target   (adversarial calls posted DIRECTLY, the attacker model)

Honor path: the call goes gate -> target -> publisher for real; the verdict is
observed via the target's read-only /received count (NOT by redelivering the
envelope), so the honor result reflects the real socket chain. Refusals are
posted directly to the target (an attacker does not route through the gate).

Run from repo root:  PYTHONPATH=. python3 EVIDENCE/proofs/g5_multiprocess_tls_001_runner.py
Exits 0 iff the honor path acts exactly once over TLS and every adversarial call
is refused with the expected REF_* reason.
"""

import datetime
import hashlib
import ipaddress
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

import requests
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.published_source import anchor_sha256

REPO = os.getcwd()
PUBLISHED_PATH = os.path.join(REPO, "EVIDENCE", "published_hashes.json")
GATE_KEY_ID = "gate-multiprocess-tls-001"


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def gen_certs(tmp):
    """Local test CA + one leaf cert (SAN 127.0.0.1 / localhost) for all three
    services. Returns (ca_path, cert_path, key_path)."""
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Elyon-Sol Test CA")])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name).issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_now() - datetime.timedelta(days=1))
        .not_valid_after(_now() + datetime.timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1")])
    san = x509.SubjectAlternativeName([
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.DNSName("localhost"),
    ])
    leaf_cert = (
        x509.CertificateBuilder()
        .subject_name(leaf_name).issuer_name(ca_cert.subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_now() - datetime.timedelta(days=1))
        .not_valid_after(_now() + datetime.timedelta(days=2))
        .add_extension(san, critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    ca_path = os.path.join(tmp, "ca.pem")
    cert_path = os.path.join(tmp, "server.crt")
    key_path = os.path.join(tmp, "server.key")
    open(ca_path, "wb").write(ca_cert.public_bytes(serialization.Encoding.PEM))
    open(cert_path, "wb").write(leaf_cert.public_bytes(serialization.Encoding.PEM))
    open(key_path, "wb").write(leaf_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    return ca_path, cert_path, key_path


def uvicorn_proc(app, port, cert, key, env, log_path):
    logf = open(log_path, "wb")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", app, "--host", "127.0.0.1",
         "--port", str(port), "--ssl-certfile", cert, "--ssl-keyfile", key,
         "--log-level", "warning"],
        cwd=REPO, env=env, stdout=logf, stderr=subprocess.STDOUT,
    )


def manifest_sha():
    return hashlib.sha256(open(os.path.join(REPO, "MANIFEST", "manifest.json"), "rb").read()).hexdigest()


def interaction(eligible=True, admin=False):
    ap = ["identity", "role", "admin"] if admin else (["identity", "role"] if eligible else [])
    return {
        "AP": ap, "OP": (["session", "request"] if eligible else []),
        "context": {}, "expected_manifest_version": "1.0",
        "expected_manifest_sha256": manifest_sha(),
    }


def main():
    tmp = tempfile.mkdtemp(prefix="g5_mptls_")
    ca, cert, key = gen_certs(tmp)
    p_port, t_port, g_port = free_port(), free_port(), free_port()
    PUB_URL = "https://127.0.0.1:%d/published_hashes.json" % p_port
    TARGET_URL = "https://127.0.0.1:%d/target" % t_port
    OTHER_URL = "https://127.0.0.1:%d/other" % t_port
    GATE_URL = "https://127.0.0.1:%d/governed-call" % g_port
    RECEIVED_URL = "https://127.0.0.1:%d/received" % t_port

    pinned_root = anchor_sha256(open(PUBLISHED_PATH, "rb").read())
    gate_priv = ed25519.Ed25519PrivateKey.generate()
    gate_pub_hex = gate_priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()

    base = dict(os.environ, PYTHONPATH=REPO)
    pub_env = dict(base)
    tgt_env = dict(base, ELYON_TARGET_URL=TARGET_URL, ELYON_PUBLISHER_URL=PUB_URL,
                   ELYON_PINNED_ROOT_SHA256=pinned_root, ELYON_GATE_KEY_ID=GATE_KEY_ID,
                   ELYON_GATE_PUBLIC_KEY_HEX=gate_pub_hex, ELYON_TLS_CA_BUNDLE=ca)
    gate_env = dict(base, ELYON_SIGNING_KEY_HEX=gate_priv.private_bytes_raw().hex(),
                    ELYON_SIGNING_KEY_ID=GATE_KEY_ID, ELYON_TLS_CA_BUNDLE=ca)

    procs = []
    try:
        services = [
            ("publisher", "IMPLEMENTATION.publisher:app", p_port, pub_env),
            ("reference_target", "IMPLEMENTATION.reference_target:app", t_port, tgt_env),
            ("gate", "IMPLEMENTATION.pep:app", g_port, gate_env),
        ]
        logpaths = []
        for _nm, _app, _port, _env in services:
            _lp = os.path.join(tmp, _nm + ".log")
            logpaths.append((_nm, _lp))
            procs.append(uvicorn_proc(_app, _port, cert, key, _env, _lp))

        def ready():
            ok = {"p": False, "t": False, "g": False}
            deadline = time.time() + 150  # generous: 3 uvicorn+TLS cold starts on a loaded CI runner
            while time.time() < deadline:
                for _nm, _pr in zip([n for n, _ in logpaths], procs):
                    if _pr.poll() is not None:
                        print("SERVICE PROCESS DIED EARLY: %s (exit %s)" % (_nm, _pr.returncode))
                        return False
                try:
                    if not ok["p"]:
                        ok["p"] = requests.get(PUB_URL, verify=ca, timeout=2).status_code == 200
                    if not ok["t"]:
                        ok["t"] = requests.get(RECEIVED_URL, verify=ca, timeout=2).status_code == 200
                    if not ok["g"]:
                        r = requests.post(GATE_URL, json={"target_url": TARGET_URL,
                                          "interaction": interaction(False)}, verify=ca, timeout=3)
                        ok["g"] = r.status_code in (200, 403)
                    if all(ok.values()):
                        return True
                except Exception:
                    pass
                time.sleep(0.5)
            return False

        if not ready():
            print("SERVICES NOT READY")
            for _nm, _lp in logpaths:
                try:
                    _tail = open(_lp, "r", errors="replace").read()[-2000:]
                except Exception as _e:
                    _tail = "<no log: %s>" % _e
                print("----- %s service log (tail) -----\n%s" % (_nm, _tail))
            return 2

        def received():
            return requests.get(RECEIVED_URL, verify=ca, timeout=5).json()["count"]

        def post_target(envelope, body):
            headers = {}
            if envelope is not None:
                headers["X-Elyon-Sol-Envelope"] = canonical_json(envelope)
            r = requests.post(TARGET_URL, json=body, headers=headers, verify=ca, timeout=10)
            if r.status_code == 200:
                return True, r.json().get("reason")
            return False, r.json().get("detail", {}).get("reason")

        results = []
        def check(label, got, exp):
            ok = got == exp
            results.append(ok)
            print("[%s] %s" % ("PASS" if ok else "FAIL", label))
            print("       got=%s expected=%s" % (got, exp))

        print("=" * 74)
        print("G5 MULTI-PROCESS + REAL-TLS chain (VL-063, artifact 12 steps 2-3 in-env)")
        print("=" * 74)
        print("local test CA    :", ca)
        print("publisher (proc) :", PUB_URL)
        print("target    (proc) :", TARGET_URL)
        print("gate      (proc) :", GATE_URL)
        print("pinned anchor    :", pinned_root)
        print("-" * 74)

        recv0 = received()

        # HONOR: real chain gate -> target -> publisher over TLS; observe via /received.
        hr = requests.post(GATE_URL, json={"target_url": TARGET_URL,
                           "interaction": interaction(True)}, verify=ca, timeout=15)
        honor_env = hr.json().get("envelope") if hr.status_code == 200 else None
        time.sleep(0.5)
        recv1 = received()
        check("honor: gate->target->publisher over TLS, target acted exactly once",
              (hr.status_code, recv1 - recv0), (200, 1))

        # Capture a swap envelope (bound to a different target_url) via the gate.
        sr = requests.post(GATE_URL, json={"target_url": OTHER_URL,
                           "interaction": interaction(True)}, verify=ca, timeout=15)
        swap_env = sr.json().get("envelope") if sr.status_code == 200 else None

        # ADVERSARIAL calls posted DIRECTLY to the target over TLS (the attacker model).
        forge = {k: v for k, v in honor_env.items() if k != "issuer_signature"} if honor_env else None
        h, r = post_target(forge, interaction(True))
        check("forge (no signature) direct-to-target over TLS", (h, r), (False, "REF_VERIFY_SIGNATURE_INVALID"))

        h, r = post_target(honor_env, interaction(True, admin=True))
        check("replay: honor envelope vs divergent interaction", (h, r), (False, "REF_VERIFY_BINDING_MISMATCH"))

        h, r = post_target(swap_env, interaction(True))
        check("target_url swap (envelope bound to /other)", (h, r), (False, "REF_VERIFY_BINDING_MISMATCH"))

        h, r = post_target(None, interaction(True))
        check("absent envelope (A1) direct-to-target", (h, r), (False, "REF_VERIFY_ENVELOPE_ABSENT"))

        recv_final = received()
        check("no adversarial call acted (received unchanged after refusals)", recv_final, recv1)

        print("-" * 74)
        ok = all(results)
        print("RESULT:", "ALL INVARIANTS HOLD (real-TLS multi-process chain)" if ok else "INVARIANT VIOLATION")
        return 0 if ok else 1
    finally:
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
