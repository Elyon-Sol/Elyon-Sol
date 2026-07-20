# Spin up your own Elyon-Sol surface

The public demo surface at **elyon-sol.io** (gate / target / sidecar / publisher) was retired on
**2026-07-20**. Everything it ran is open source (AGPL-3.0), so you can stand up the identical
four-service admission surface yourself — locally in about two commands, or on your own hosts —
and run the same "break-it" walkthrough against your own instance.

This is the reproducible version of what the site's **Break it in 60 seconds** section used to
point at. None of it needs the retired public nodes.

## What you get

| Service   | Local URL               | What it does                                                  |
|-----------|-------------------------|--------------------------------------------------------------|
| gate      | `http://localhost:8000` | PEP: validates schema, evaluates admissibility, signs every ELIGIBLE, forwards |
| target    | `http://localhost:9000` | reference enforcing target: verifies the envelope, acts exactly once on honor |
| publisher | `http://localhost:9100` | serves the hash-locked published record                      |
| sidecar   | `http://localhost:9200` | OPA-style ext-authz ALLOW/DENY (optional overlay)            |

## Fast path — local, with Docker

Prereqs: `git`, Docker (with `docker compose`), plus `curl` + `jq` to poke it.

```bash
git clone https://github.com/Elyon-Sol/Elyon-Sol.git
cd Elyon-Sol

# 1. Generate the out-of-band trust material (gate keypair + pinned-root anchor).
#    Writes deploy/.env (git-ignored). One time.
python deploy/bootstrap_config.py

# 2. Bring up gate + target + publisher.
cd deploy && docker compose up --build
```

That's the three-service core on `localhost:8000 / :9000 / :9100`. To add the ext-authz sidecar
(`localhost:9200`) as well:

```bash
docker compose -f docker-compose.yml -f docker-compose.authz.yml up --build
```

No Docker? Each service is a plain `uvicorn` app — run `IMPLEMENTATION.pep:app`,
`IMPLEMENTATION.reference_target:app`, and `IMPLEMENTATION.publisher:app` on those ports with the
`deploy/.env` values in the environment (see `deploy/runbook.md`).

## Break it — against your own instance

Point the walkthrough at your local gate/target instead of the retired public hosts:

```bash
export GATE=http://localhost:8000
export TARGET=http://localhost:9000
export AUTHZ=http://localhost:9200     # only if you brought up the sidecar overlay
```

Then follow **`deploy/BREAK_IT_IN_60_SECONDS.md`**: mint a governed call at `$GATE/governed-call`,
present the returned envelope to `$TARGET/target` (it acts once), then try the refusals — no token,
replay, forge a byte, rebind the action, or get the sidecar to ALLOW. The manifest pin in that
walkthrough (`expected_manifest_sha256`) matches the repo's committed `MANIFEST/manifest.json`, so
it is valid against any instance you build from this checkout. Adjudicate a suspected break with
**`deploy/INSPECT_YOUR_BREAK.md`** — the inspector reads your token the way the target does.

## Overlays (optional)

Each is a compose overlay on top of the base file (`-f docker-compose.yml -f <overlay>`):

- **TLS** (`docker-compose.tls.yml`) — real certs on every hop; cert generation in `deploy/tls/`, walk-through in `deploy/runbook.md` §5.
- **ext-authz sidecar + Envoy + OPA** (`docker-compose.authz.yml`) — the OPA-style deployment (Mode A: elyon-authz first, OPA second).
- **shared replay store** (`docker-compose.replay.yml`) — Redis-backed exactly-once under horizontal scale.
- **governance / human-in-the-loop** (`docker-compose.governance.yml`) — the `202 PENDING_APPROVAL` approval layer + mTLS; see `deploy/GOVERNANCE_DEPLOYMENT.md`. The operator console for this is **GLESAC** (https://github.com/Elyon-Sol/GLESAC).

## Your own hosts / cloud

`deploy/runbook.md` §3–4 covers running the services across real hosts (replace the compose
service-name URLs with hostnames/IPs and distribute the pinned anchor out-of-band) and on a
container platform (ECS/Fargate, Cloud Run, k8s). `deploy/LIVE_BRINGUP_RUNBOOK.md` is the fuller
bring-up the public surface used, and `deploy/tls/` + `docker-compose.tls.yml` add real TLS.

## Note

Active development of this project is retired; the code is AGPL-3.0 and yours to run, fork, and
build on. Spinning this up reproduces the reference surface — it does **not** re-open the credited
red-team challenge, which is closed.
