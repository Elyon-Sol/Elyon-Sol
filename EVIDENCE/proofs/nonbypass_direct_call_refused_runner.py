"""
Feature 2 non-bypassable proof, REAL SOCKETS (design 2.3 / 2.4).

Stands up a TLS target on 127.0.0.1 that REQUIRES a CA-signed client cert
(mTLS), then shows over real TCP:
  1. a DIRECT connection WITHOUT the gate client cert is refused at the TLS
     handshake - the target REJECTS it at the transport and the app is never
     reached;
  2. a connection presenting the gate client cert is honored and the target
     sees the gate's identity.

The authoritative signal is the SERVER side: whether the target ever accepted
the connection into app logic. (On TLS 1.3 the client's handshake can return
before the server's client-auth rejection propagates, so the client-side
exception is not relied upon.) Hermetic: a private dev CA generated in-process,
loopback only. Exit 0 iff the bypass is refused server-side AND the gate call is
honored server-side.
"""

import queue
import socket
import ssl
import sys
import tempfile
import threading
import os

import deploy.tls.gen_certs as g

TARGET_HOST = "target.elyon.local"
GATE_CN = "gate.elyon.local"


def _write(d, n, b):
    p = os.path.join(d, n); open(p, "wb").write(b); return p


def main():
    ca_key, ca_cert = g.gen_ca("Elyon-Sol Dev CA")
    ca_pem = g.cert_pem(ca_cert)
    tk, tc = g.gen_leaf(ca_key, ca_cert, TARGET_HOST, [TARGET_HOST, "127.0.0.1"])
    gk, gc = g.gen_leaf(ca_key, ca_cert, GATE_CN, [GATE_CN])
    tmp = tempfile.mkdtemp()
    t_crt = _write(tmp, "t.crt", g.cert_pem(tc)); t_key = _write(tmp, "t.key", g.key_pem(tk))
    ca_f = _write(tmp, "ca.pem", ca_pem)
    g_crt = _write(tmp, "g.crt", g.cert_pem(gc)); g_key = _write(tmp, "g.key", g.key_pem(gk))

    s_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    s_ctx.load_cert_chain(t_crt, t_key)
    s_ctx.verify_mode = ssl.CERT_REQUIRED          # the gate-only door (mTLS)
    s_ctx.load_verify_locations(ca_f)

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind(("127.0.0.1", 0)); lsock.listen(5)
    port = lsock.getsockname()[1]
    results = queue.Queue()

    def serve(n):
        for _ in range(n):
            try:
                raw, _ = lsock.accept()
            except OSError:
                return
            try:
                tls = s_ctx.wrap_socket(raw, server_side=True)
                # reached app logic: record who connected
                results.put(("ACCEPTED", tls.getpeercert()))
                try: tls.close()
                except OSError: pass
            except ssl.SSLError as e:
                # rejected at the TLS layer - the app was never reached
                results.put(("REFUSED_AT_TLS", str(e)))
                try: raw.close()
                except OSError: pass

    th = threading.Thread(target=serve, args=(2,), daemon=True); th.start()

    def connect(with_cert):
        c_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        c_ctx.load_verify_locations(ca_f)
        c_ctx.check_hostname = True
        c_ctx.verify_mode = ssl.CERT_REQUIRED
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            c_ctx.verify_flags |= ssl.VERIFY_X509_STRICT
        if with_cert:
            c_ctx.load_cert_chain(g_crt, g_key)
        try:
            raw = socket.create_connection(("127.0.0.1", port), timeout=5)
            tls = c_ctx.wrap_socket(raw, server_hostname=TARGET_HOST)
            try: tls.recv(1)            # force any post-handshake alert to surface
            except ssl.SSLError: pass
            tls.close()
        except (ssl.SSLError, OSError):
            pass

    # 1) direct bypass (no client cert)
    connect(with_cert=False)
    r1 = results.get(timeout=5)
    # 2) routed through the gate (client cert)
    connect(with_cert=True)
    r2 = results.get(timeout=5)

    lsock.close(); th.join(timeout=2)

    bypass_refused = (r1[0] == "REFUSED_AT_TLS")
    gate_peer = r2[1] if r2[0] == "ACCEPTED" else None
    gate_honored = gate_peer is not None
    saw_gate = bool(gate_peer) and \
        dict(x[0] for x in gate_peer.get("subject", ())).get("commonName") == GATE_CN

    print("server verdict, bare connection :", r1[0], "(bypass refused at TLS)" if bypass_refused else "")
    print("server verdict, gate connection :", r2[0])
    print("target saw gate identity        :", saw_gate)
    ok = bypass_refused and gate_honored and saw_gate
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
