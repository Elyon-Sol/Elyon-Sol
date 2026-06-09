# Elyon-Sol deployment runbook (C1 / VL-081)

Stands up the gate / reference target / publisher as networked services. C1 is plain HTTP (the
dev / loopback model); real TLS + certs are C2. The container layer is UNVALIDATED in the build
sandbox (no docker) - this runbook is the author's stand-up path, and the documented stand-up is
the acceptance referent the sandbox cannot provide.

## What the three services are

- `publisher` (:9100) - serves the committed, hash-locked record `EVIDENCE/published_hashes.json`
  verbatim at `/published_hashes.json`. Trust is not in the transport: the target anchor-verifies
  the fetched bytes against its pinned root, so a tampered record fails closed.
- `target` (:9000) - the reference enforcing target. Fetches the record, anchor-verifies, runs the
  production `verify_envelope` (signature -> reassert/currency -> binding -> freshness), acts on a
  call exactly once on honor and never on refuse.
- `gate` (:8000) - the PEP. Validates schema, evaluates admissibility, SIGNS every ELIGIBLE
  forward, and pushes it to the target with the envelope header.

All three are existing modules configured ONLY by environment - no code changes for deployment.

## 1. Generate the out-of-band config (once)

    python deploy/bootstrap_config.py        # writes deploy/.env (git-ignored)

This generates a gate Ed25519 keypair and computes the pinned-root anchor from the committed
record. The target pins the public half + the anchor; the gate signs with the private half. The
`.env` is the out-of-band trust material - never commit it; distribute the pinned anchor securely
(its secure distribution is the named G5 floor).

## 2. Single box (docker compose)

    cd deploy
    docker compose up --build

Smoke test (a valid admitted call flows gate -> target; the target acts once):

    # admit a decision at the gate, capture the envelope, present it to the target
    # (the client mints interaction = the call it intends, target_url = the gate's
    #  ELYON_TARGET_URL; see EVIDENCE/proofs/attack_harness.py HttpSurface for the shape)

The gate fails closed with no signing key (REF_PEP_FAIL_CLOSED); the target fails closed with no /
bad config (REF_TARGET_NOT_CONFIGURED); the publisher 503s with no record.

## 3. Two real hosts (the G5 direction)

Run the publisher + target on host B and the gate on host A (or each on its own host). Replace the
compose service-name URLs with real hostnames/IPs:
- `ELYON_TARGET_URL` and the gate's forward target -> `https://<hostB>:9000/target`
- `ELYON_PUBLISHER_URL` -> `https://<hostB>:9100/published_hashes.json`

Open :8000 (gate), :9000 (target), :9100 (publisher) between the hosts. Distribute the pinned
anchor and the gate public key to the target host out-of-band (not over the same channel as the
record). This is where C1 (plain HTTP) becomes the G5 floor only once C2 (real TLS) is layered on.

## 4. Cloud

Each service is a stateless container; deploy as three services behind the platform's networking
(ECS/Fargate, Cloud Run, k8s Deployments + Services). Inject the `.env` values as the platform's
secrets, not as image layers. The pinned anchor + gate public key are configuration, not secrets,
but must be delivered out-of-band relative to the record.

## 5. Real TLS (C2 preview - not built here)

C2 promotes the plain-HTTP hops to real TLS. The hooks already exist in `IMPLEMENTATION/transport.py`:
- `ELYON_TLS_CA_BUNDLE` - the CA bundle the gate/target client trusts.
- `ELYON_TLS_CLIENT_CERT` - `certfile` or `certfile:keyfile` for mutual TLS.

Serve each app under TLS with `uvicorn --ssl-certfile <cert> --ssl-keyfile <key>` and point the
clients at the CA bundle. Real certs (a real CA / Let's Encrypt) + the anchor/key trust-bootstrap
runbook are C2's deliverable; this section names the seam, it does not provide the certs.

## Honest status

The config bootstrap is validated in-sandbox (its output round-trips admit -> verify -
`TESTS/deploy/test_bootstrap_config.py`). The docker image, the compose stand-up, and the
two-host / TLS path are NOT validated here (no docker, no real hosts, no real CA). Standing them
up - and running the VL-079 attack suite over that real surface (C3 live) - is the author's, and
is the gate-1 referent external readiness actually needs.
