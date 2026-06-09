# Trust bootstrap (C2 / VL-082) - distributing trust out-of-band

TLS authenticates the TRANSPORT. It does NOT replace Elyon-Sol's anchor: the target
anchor-verifies the fetched record against a pinned root, so even a TLS-terminating proxy that
swaps the record fails closed. Three pieces of trust material travel out-of-band, each on a
channel SEPARATE from the served record (so a transport compromise does not also deliver trust):

1. The CA bundle (`ca.crt`) - what the gate/target clients trust to verify their TLS peers.
   With a PUBLIC CA (Let's Encrypt), there is no bundle to ship: clients trust the system store
   and `ELYON_TLS_CA_BUNDLE` is left unset.
2. The pinned-root anchor (`ELYON_PINNED_ROOT_SHA256`) - sha256 of the committed published record.
   The target holds it out-of-band; it is the trust floor under the record, independent of TLS.
3. The gate public key + key_id (`ELYON_GATE_PUBLIC_KEY_HEX` / `ELYON_GATE_KEY_ID`) - what the
   target pins to verify the gate's signature.

Root/publisher key COMPROMISE recovery remains irreducibly out-of-band (the named floor); TLS does
not change that.

## Path A - private dev CA (closed network)

    python deploy/tls/gen_certs.py                 # CA + gate/target/publisher leaves
    # or, with real hostnames as extra SANs:
    python deploy/tls/gen_certs.py host-a.internal host-b.internal

Ship `ca.crt` to every client host out-of-band; keep each `*.key` only on its own service host.
Run with the TLS overlay (see docker-compose.tls.yml header). Good for a closed two-host network;
NOT a public-network, externally-attacked surface.

## Path B - real / Let's Encrypt CA (public network)

Obtain real certs for the real hostnames (certbot / ACME). Mount them where the overlay expects
(`/certs/<svc>.crt|.key`) or adjust the overlay paths. Clients trust the system store, so unset
`ELYON_TLS_CA_BUNDLE`. This is the path toward a real public surface; standing it up and pointing
the VL-079 attack suite at it (C3 live) is the author's.

## Optional - mutual TLS

Set `ELYON_TLS_CLIENT_CERT` (`certfile` or `certfile:keyfile`) on the gate/target clients to
present a client cert; the leaves emitted by gen_certs carry CLIENT_AUTH EKU for this.

## Honest status

The cert material and a verified TLS handshake are checked in-sandbox
(`TESTS/deploy/test_tls_certs.py`). A real two-host TLS run, a real / Let's Encrypt CA, and a real
external attacker on that surface are NOT (AUTHOR / the G5 floor). TLS hardens the transport; it
does not move the external-validation axis past the author's real run.
