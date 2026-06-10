# Three-Domain POC — live-drive runbook (VL-096)

Drives the synthetic three-domain POC against the real two-VM deployment
(gate on VM-A, publisher + reference target on VM-B), one domain at a time.
Because the gate evaluates the **single** on-disk `MANIFEST/manifest.json`, the
three domains cannot run at once: each domain pins its own manifest, then runs.

Prereq: the cross-host signed-mode deployment from
`deploy/host_setup_virtualbox.md` is already standing (gate :8000, target :9000,
publisher :9100, dev-CA TLS). The committed in-process reports
(`reports/*_report.md`, mode: inproc) show the expected outcomes — the live run
reproduces them over real transport (characterization, GR-3; not external
certification).

The runner is driven from the client (the Windows git-bash host with the repo).
It needs Python with `requests` and the repo on `PYTHONPATH`; it makes no use of
the sandbox.

---

## Per-domain procedure (repeat for medical, legal, finance)

Let `DOMAIN` ∈ {medical, legal, finance} and `M=EVIDENCE/proofs/three_domain_poc/manifests/$DOMAIN.json`.

### 1. Pin the domain manifest on BOTH hosts (byte-identical)

The gate reads the manifest to evaluate; the publisher hashes it into the
published record the target checks currency against. They must match.

On **VM-A** (gate) and **VM-B** (publisher/target), in the repo root:

    cp EVIDENCE/proofs/three_domain_poc/manifests/$DOMAIN.json MANIFEST/manifest.json

(They are the same committed file, so both hosts get identical bytes and the
same `manifest_sha256`.)

### 2. Rebuild/restart so the new manifest takes effect

On **VM-A**:

    docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.tls.yml \
        -f deploy/docker-compose.hosts.yml up -d --build gate

On **VM-B** (republish the signed record with the new manifest sha, restart the
publisher; the target re-fetches per request so it needs no restart):

    docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.tls.yml \
        -f deploy/docker-compose.hosts.yml up -d --build publisher

`--build` guarantees the change is picked up whether the manifest is baked into
the image or volume-mounted.

### 3. Run the POC for this domain (from the client)

    PYTHONPATH=. python3 -m EVIDENCE.proofs.three_domain_poc.poc_runner \
        --mode live \
        --gate-url   https://<VM-A-ip>:8000 \
        --target-url https://<VM-B-ip>:9000 \
        --domain     $DOMAIN \
        --ca-bundle  deploy/tls/certs/ca.crt \
        --decision-max-age <the gate's ELYON_DECISION_MAX_AGE_SECONDS>

Notes:
- `--ca-bundle` is the dev CA so the client verifies the gate/target certs
  (fail-closed; never pass `verify=False`).
- `--decision-max-age` must equal the gate's configured decision window so the
  `stale_decision` case can wait it out. For a quick run set the gate's
  `ELYON_DECISION_MAX_AGE_SECONDS=5` in `deploy/.env`, rebuild the gate (step 2),
  and pass `--decision-max-age 5`. If omitted, `stale_decision` records SKIPPED
  (it is proven deterministically in the in-process report).
- The live `target_url` is the real deployed target; the report's bound URLs are
  the real deployment URLs (not the illustrative `*.example` ones used in-process).

The runner writes `reports/$DOMAIN_report.md` (mode: **live**) and prints a
per-case pass/fail line. Exit code is non-zero if any case's outcome differs
from the expected production reason.

### 4. Collect the report

`EVIDENCE/proofs/three_domain_poc/reports/$DOMAIN_report.md` is the reviewer
artifact for that domain over real transport.

---

## After all three

Restore the repository's canonical manifest on both hosts and rebuild, so the
deployment returns to its default state:

    git checkout MANIFEST/manifest.json
    docker compose ... up -d --build gate publisher   # (the same -f stack)

And restore `ELYON_DECISION_MAX_AGE_SECONDS` to its normal value (300) if you
shortened it for the stale case.

## What a live pass shows (and does not)

Shows: the same one production chain admits/refuses domain-shaped inputs over
real cross-host TLS exactly as the in-process reports predict, for three
unrelated domains. Does not: move G5 — these are still the author's own calls on
a private network with a dev CA. The open road item remains a real external
attacker on a real public surface.
