# 21 - Real TLS / certs + trust bootstrap (C2)

Repo path: docs/restructure/21_real_tls_and_trust_bootstrap_spec.md. Increment VL-082 (C2,
artifact 13 Phase C). Layers real TLS onto the C1 packaging and documents the out-of-band trust
bootstrap (CA bundle + pinned anchor + gate public key).

## 1. Purpose and scope, and the honest locus split

Artifact 13 C2: "promote the local test-CA to real certs (real CA / Let's Encrypt) + an
out-of-band anchor/key distribution runbook. Acceptance: cert scripts + runbook; the chain
verified over real TLS. Locus: AUTHOR (real hosts)."

The locus split (as in C1): the cert TOOLING and the TLS overlay are authored in-house; the
real cross-host TLS run is the author's. What CAN be validated in-sandbox - and is - is that the
generated cert MATERIAL is correct: the CA signs the leaf, the chain is well-formed, and a REAL
TLS handshake (driven over an in-memory BIO, no sockets/processes) between a server holding the
leaf and a client trusting the CA SUCCEEDS and verifies the peer - while a client trusting a
DIFFERENT CA is REFUSED (fail-closed). That handshake is C2's sandbox-green referent; a real
two-host TLS run, and a real / Let's Encrypt CA, are the author's.

In scope (VL-082):
- `deploy/tls/gen_certs.py`: generates a private dev CA and per-service leaf certs (SANs for the
  compose service names + localhost) using the `cryptography` library (no openssl binary
  dependency; the CI-pinned crypto stack). For a real deployment the operator either regenerates
  with real hostnames under this private CA (closed network) or uses a real / Let's Encrypt CA
  (public network) - the runbook covers both.
- `deploy/docker-compose.tls.yml`: a compose OVERLAY (`-f docker-compose.yml -f
  docker-compose.tls.yml`) that serves each service under `uvicorn --ssl-*`, mounts the certs,
  flips the URLs to `https://`, and points the gate/target clients at the CA bundle via the
  existing `transport.py` `ELYON_TLS_CA_BUNDLE` / `ELYON_TLS_CLIENT_CERT` hooks. UNVALIDATED
  container layer (no docker).
- `deploy/tls/trust_bootstrap.md`: the out-of-band distribution runbook - the CA bundle, the
  pinned-root anchor, and the gate public key + key_id, each delivered on a channel SEPARATE from
  the served record (so transport compromise does not also deliver the trust material).
- `TESTS/deploy/test_tls_certs.py`: the chain validates (CA self-signed + CA:TRUE; leaf signed by
  the CA, in-window, expected SAN); a real in-memory TLS handshake with the generated certs
  verifies the server; a wrong-CA client refuses.

Out of scope (named): a real / Let's Encrypt CA and a real two-host TLS run (AUTHOR); the live
attack-suite run over that surface (C3 live); the real-transport readiness predicate (C4); the
docker stand-up (no docker in-sandbox).

## 2. How TLS wires onto the existing code (no code change)

The transport seam (`IMPLEMENTATION/transport.py`, VL-039) already resolves TLS from the
environment, fail-closed (verify defaults ON): `ELYON_TLS_CA_BUNDLE` (the CA the gate/target
client trusts) and `ELYON_TLS_CLIENT_CERT` (`certfile` or `certfile:keyfile` for mutual TLS).
Serving under TLS is uvicorn's `--ssl-certfile` / `--ssl-keyfile`. So C2 is CONFIGURATION over the
C1 services: no module changes. A peer that cannot be verified raises an SSL error that the
existing fail-closed catches map to a refusal (the gate's upstream catch; the target's fetch
`except Exception: return None` -> REF_TARGET_ANCHOR_MISMATCH).

## 3. Trust bootstrap (the out-of-band discipline)

TLS authenticates the TRANSPORT; it does not replace Elyon-Sol's anchor. Three pieces travel
out-of-band, each on a channel separate from the served record:
- the CA bundle (or, with a public CA, nothing - the system trust store suffices);
- the pinned-root anchor (`ELYON_PINNED_ROOT_SHA256`) - the target anchor-verifies the fetched
  record against it, so a TLS-terminating proxy that swaps the record still fails closed;
- the gate public key + key_id (`ELYON_GATE_PUBLIC_KEY_HEX` / `ELYON_GATE_KEY_ID`).
Root/publisher key COMPROMISE recovery stays irreducibly out-of-band (the named floor).

## 4. Fail-closed / no new invariant

No code changes; TLS is verification I/O (canon section 14). Verification defaults ON
(transport.py); weakening requires an explicit env value. A misconfigured or unverifiable peer
fails closed per the existing catches. No canon / evaluator / MANIFEST / envelope change.
Build-then-wire: new deploy/tls/ artifacts + overlay only; the default path is byte-unchanged.

## 5. Honest ceiling

The cert tooling and the in-memory handshake are validated in-sandbox; a real two-host TLS run, a
real / Let's Encrypt CA, and a real external attacker on that surface are NOT (AUTHOR / the G5
floor). A private dev CA over a closed network is still not the public-network, externally-attacked
referent external readiness needs; it is the transport layer the attack suite (C3 live) then runs
over. TLS hardens the transport; it moves the external-validation axis no further than the
author's real run does.

## 6. Acceptance (VL-082)

- `TESTS/deploy/test_tls_certs.py`: `gen_certs` produces a valid chain (CA self-signed + CA:TRUE;
  leaf CA-signed, in-window, expected SAN); a real in-memory TLS handshake with the generated
  server cert + a CA-trusting client SUCCEEDS and verifies the peer; a client trusting a different
  CA is REFUSED (fail-closed).
- `deploy/tls/gen_certs.py`, `deploy/docker-compose.tls.yml`, `deploy/tls/trust_bootstrap.md`
  committed; the certs/keys themselves are git-ignored.
- Full suite green; the default path byte-unchanged.
