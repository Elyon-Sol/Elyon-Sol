# 20 - Deploy packaging (C1)

Repo path: docs/restructure/20_deploy_packaging_spec.md. Increment VL-081 (C1, artifact 13 Phase
C). Packages the gate / reference target / publisher as networked services (docker-compose) with
an out-of-band config bootstrap and a two-real-host / cloud runbook.

## 1. Purpose and scope, and the honest locus split

Artifact 13 C1: "a docker-compose (gate / reference target / publisher as networked services) + a
two-real-host / cloud runbook. Acceptance: compose + runbook committed; a documented stand-up.
Locus: AUTHOR (docker absent from the sandbox; validated on real hosts)."

The locus split is load-bearing and stated up front. The build sandbox has NO docker, so the
container orchestration CANNOT be validated here - the `deploy/Dockerfile` and
`deploy/docker-compose.yml` ship as UNVALIDATED drafts whose stand-up is the author's (the
"documented stand-up" half of the acceptance). What CAN be built and validated in-sandbox is the
out-of-band CONFIG bootstrap: generating the gate keypair, computing the pinned-root anchor, and
proving the generated config is internally consistent (the public key the target pins matches the
gate's signing key; the anchor matches the served record) by a round-trip admit -> verify. That
round-trip is C1's sandbox-green referent; the container layer is not.

In scope (VL-081):
- `deploy/Dockerfile`: one image (repo + pinned deps) serving any of the three uvicorn entrypoints
  by command override. UNVALIDATED (no docker).
- `deploy/docker-compose.yml`: three networked services - `publisher` (serves the committed
  record), `target` (the reference enforcing target), `gate` (the PEP) - wired by the existing
  `ELYON_*` env contract, reading secrets from a `.env`. Structurally validated (YAML parse +
  entrypoints reference real `IMPLEMENTATION.<mod>:app`); NOT run.
- `deploy/bootstrap_config.py`: generates a gate Ed25519 keypair, computes the pinned-root anchor
  from the committed record, and writes a `.env` of the `ELYON_*` values the three services read.
  VALIDATED in-sandbox by a round-trip test.
- `deploy/runbook.md`: the single-box (compose) and two-real-host / cloud stand-up, plus the C2
  TLS bootstrap preview (real certs are C2, not built here).
- `TESTS/deploy/test_bootstrap_config.py`: the generated config round-trips - an envelope signed
  with the bootstrap signing key, presented for the matching interaction, is HONORED by
  `verify_envelope` against the bootstrap pinned key + the committed record; tampering the args is
  refused; the compose file parses and its commands name real module apps.

Out of scope (named): real TLS / certs + the trust bootstrap (C2); the live cross-host stand-up and
the attack-suite run over real transport (C3 live, AUTHOR); the real-transport readiness predicate
(C4). docker image build / run (no docker in-sandbox).

## 2. The service topology and the env contract

Three services, each an existing module's uvicorn `app`, configured ONLY by environment (the
modules already read these; no code change):
- `publisher`  - `uvicorn IMPLEMENTATION.publisher:app` :9100; `ELYON_PUBLISHED_RECORD` (the
  committed record path). Serves `/published_hashes.json` verbatim.
- `target`     - `uvicorn IMPLEMENTATION.reference_target:app` :9000; `ELYON_TARGET_URL`,
  `ELYON_PUBLISHER_URL`, `ELYON_PINNED_ROOT_SHA256`, `ELYON_GATE_KEY_ID`,
  `ELYON_GATE_PUBLIC_KEY_HEX`. Fetches the record, anchor-verifies, runs `verify_envelope`.
- `gate`       - `uvicorn IMPLEMENTATION.pep:app` :8000; `ELYON_SIGNING_KEY_HEX`,
  `ELYON_SIGNING_KEY_ID`, `ELYON_DECISION_MAX_AGE_SECONDS`. Signs every ELIGIBLE forward.

The trust material is out-of-band (never committed): the gate's private signing key, the public
half the target pins, and the pinned-root anchor. `bootstrap_config.py` generates them into a
`.env` the compose file reads; `.env` is git-ignored.

## 3. Fail-closed / no new invariant

No code changes; the services are the existing apps, configured by env. A misconfigured service
fails closed per its module (the gate with no key -> REF_PEP_FAIL_CLOSED; the target with no/ bad
config -> REF_TARGET_NOT_CONFIGURED; the publisher with no record -> 503). No canon / evaluator /
MANIFEST / envelope change (canon section 14). Build-then-wire: new deploy/ artifacts only; the
default path is byte-unchanged.

## 4. Honest ceiling

The compose + Dockerfile are UNVALIDATED in-sandbox (no docker); their stand-up is the author's,
and over plain HTTP they are the loopback model, not the G5 real-transport floor. Real TLS + certs
(C2) and a real external attacker (the binding NOT-READY reason) are not provided here. The only
sandbox-green referent C1 earns is the config bootstrap's admit->verify round-trip; the container
orchestration earns none until the author stands it up.

## 5. Acceptance (VL-081)

- `TESTS/deploy/test_bootstrap_config.py`: the bootstrap config round-trips (signed envelope
  honored against the bootstrap pinned key + committed record; tampered args refused); the
  compose file parses and its service commands name real `IMPLEMENTATION.<mod>:app` entrypoints.
- `deploy/bootstrap_config.py` runs and writes a `.env` whose `ELYON_PINNED_ROOT_SHA256` equals
  `anchor_sha256` of the committed record and whose `ELYON_GATE_PUBLIC_KEY_HEX` matches
  `ELYON_SIGNING_KEY_HEX`.
- `deploy/Dockerfile`, `deploy/docker-compose.yml`, `deploy/runbook.md` committed (UNVALIDATED
  container layer; AUTHOR stand-up).
- Full suite green; the default path byte-unchanged.
