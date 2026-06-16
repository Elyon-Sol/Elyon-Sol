# Live public-surface bring-up runbook (artifact 29 Phase 1)

Two real VPS hosts + your domain + Let's Encrypt. Closes Gate 1 and retires the
dev-CA ceiling. Consolidates deploy/runbook.md section 3, deploy/tls/trust_bootstrap.md
Path B, and EVIDENCE/proofs/attack_suite_live_runner.py into one ordered procedure.

Notation: replace `EXAMPLE.COM` with your domain throughout (the domain is set:
`elyon-sol.io`).
- Host A = the gate.        DNS: gate.EXAMPLE.COM
- Host B = target + publisher. DNS: target.EXAMPLE.COM (also serves the publisher)

> CANONICAL PORTS (aligned to deploy/G5_GO_LIVE.md and the attacker pack):
> gate **8443**, target **9443**, publisher **9143**, sidecar **9243**. The
> services MUST bind these ports because they are the URLs the attacker pack
> publishes. This runbook has been updated to 8443/9443/9143 below.
>
> SIDECAR GAP: this runbook predates the VL-104/105 ext-authz sidecar
> (authz.elyon-sol.io:9243, host B). Its bring-up is NOT yet folded in here -
> follow deploy/G5_GO_LIVE.md section 2 step 4 plus docker-compose.authz.yml +
> docker-compose.authz.tls.yml for the sidecar, and add a 4th DNS A-record
> (authz.EXAMPLE.COM -> <IP_B>) and open port 9243 on host B.

---

## 0. Provision (once)

1. Two small VPS instances on different networks (Hetzner CX22 ~EUR4, or DigitalOcean/
   Vultr ~$6). Ubuntu 22.04+. Note their public IPv4s: <IP_A>, <IP_B>.
2. DNS A-records at your registrar:
       gate.EXAMPLE.COM    -> <IP_A>
       target.EXAMPLE.COM  -> <IP_B>
   Wait for propagation (`dig +short gate.EXAMPLE.COM` returns <IP_A>).
3. On BOTH hosts: install docker + compose plugin, and certbot.
       curl -fsSL https://get.docker.com | sh
       sudo apt-get update && sudo apt-get install -y certbot
4. Firewall: open 22 (ssh), and the service ports only where needed:
   - Host A: 8443 (gate, public - this is the attack surface)
   - Host B: 9443 (target) and 9143 (publisher) reachable from Host A AND from the
     internet (the attacker hits the target directly too, per claim-sheet A1 tests)
   - 80/tcp on both during cert issuance (certbot standalone)

## 1. Real certs (Let's Encrypt - Path B, no dev CA)

On Host A:
    sudo certbot certonly --standalone -d gate.EXAMPLE.COM
On Host B:
    sudo certbot certonly --standalone -d target.EXAMPLE.COM
Certs land in /etc/letsencrypt/live/<name>/{fullchain.pem,privkey.pem}.
Because the CA is public, clients trust the system store: LEAVE ELYON_TLS_CA_BUNDLE UNSET.

## 2. Out-of-band trust material (once, from a trusted machine)

Generate the gate key + pinned anchor (deploy/bootstrap_config.py writes deploy/.env):
    python deploy/bootstrap_config.py
This produces: ELYON_SIGNING_KEY_HEX, ELYON_SIGNING_KEY_ID (gate private half),
ELYON_GATE_PUBLIC_KEY_HEX, ELYON_GATE_KEY_ID (public half for the target),
ELYON_PINNED_ROOT_SHA256 (sha256 of EVIDENCE/published_hashes.json).

Deliver to Host B OUT OF BAND (not over the same channel as the served record):
ELYON_GATE_PUBLIC_KEY_HEX, ELYON_GATE_KEY_ID, ELYON_PINNED_ROOT_SHA256.
Keep ELYON_SIGNING_KEY_HEX on Host A ONLY. Never commit deploy/.env.

## 3. Host B - target + publisher (signed mode, real hostnames)

Clone the repo to Host B. Create deploy/.env.hostB:
    ELYON_PINNED_ROOT_SHA256=<from step 2>
    ELYON_GATE_KEY_ID=<from step 2>
    ELYON_GATE_PUBLIC_KEY_HEX=<from step 2>
    ELYON_TARGET_URL=https://target.EXAMPLE.COM:9443/target
    ELYON_PUBLISHER_URL=https://target.EXAMPLE.COM:9143/published_hashes.json

Run target + publisher under TLS (uvicorn serves the certs directly):
    # publisher
    uvicorn IMPLEMENTATION.publisher:app --host 0.0.0.0 --port 9143 \
      --ssl-certfile /etc/letsencrypt/live/target.EXAMPLE.COM/fullchain.pem \
      --ssl-keyfile  /etc/letsencrypt/live/target.EXAMPLE.COM/privkey.pem
    # target (separate shell / unit), env from .env.hostB
    uvicorn IMPLEMENTATION.reference_target:app --host 0.0.0.0 --port 9443 \
      --ssl-certfile /etc/letsencrypt/live/target.EXAMPLE.COM/fullchain.pem \
      --ssl-keyfile  /etc/letsencrypt/live/target.EXAMPLE.COM/privkey.pem
    export ELYON_ISSUANCE_LOG_PATH=/var/elyon/issuance.log   # on the GATE, see step 4

Smoke: `curl https://target.EXAMPLE.COM:9143/published_hashes.json` returns the record.

## 4. Host A - the gate (signed mode + issuance log)

Clone the repo to Host A. Create deploy/.env.hostA:
    ELYON_SIGNING_KEY_HEX=<private, from step 2>
    ELYON_SIGNING_KEY_ID=<from step 2>
    ELYON_DECISION_MAX_AGE_SECONDS=300
    ELYON_TARGET_URL=https://target.EXAMPLE.COM:9443/target
    ELYON_ISSUANCE_LOG_PATH=/var/elyon/issuance.log

    mkdir -p /var/elyon
    uvicorn IMPLEMENTATION.pep:app --host 0.0.0.0 --port 8443 \
      --ssl-certfile /etc/letsencrypt/live/gate.EXAMPLE.COM/fullchain.pem \
      --ssl-keyfile  /etc/letsencrypt/live/gate.EXAMPLE.COM/privkey.pem

The issuance log (VL-099) makes the run reconcilable: every admitted call is recorded
for the inspector's reconcile pass.

## 5. Self-test BEFORE exposure (Phase 1.4 - the critical gate)

From any machine (your laptop), run the live attack suite over the real surface:
    ELYON_LIVE_GATE_URL=https://gate.EXAMPLE.COM:8443 \
    ELYON_LIVE_TARGET_URL=https://target.EXAMPLE.COM:9443 \
    ELYON_LIVE_TARGET_ID=https://target.EXAMPLE.COM:9443/target \
    python EVIDENCE/proofs/attack_suite_live_runner.py

Expected: every gate-2 attack defeated + the positive control honored; exit 0.
- exit 0  -> the surface is real and the defenses transport. Proceed.
- exit 1  -> AN ATTACK SUCCEEDED. Do NOT expose. Capture the case, fix, re-run.
  (The VirtualBox tier found 4 real bugs this way - expect the public tier to surface
  its own. A found bug now is the process working, not failing.)

On a green run: record the run log and flip the REAL_TRANSPORT readiness predicate
green naming that log (C4). This is the author validating the surface - NOT yet the
external validation.

## 6. Only after green: invite the attacker (Phase 3.1 / 4 / 5)

Hand the individual researcher the briefing pack (RED_TEAM_BRIEFING.md) - live URLs,
the claim sheet, the named floors, the inspector 


## Deployment-posture notes (VL-110 cross-model round; named-open items)
- R-02 (replay across instances): the default replay cache is PER-PROCESS. For >1 worker/replica,
  set ELYON_REPLAY_REDIS_URL (a shared store). If you run multi-instance, also set
  ELYON_REPLAY_MULTI_INSTANCE=1 so a missing shared store FAILS CLOSED at startup instead of
  silently giving each process its own cache. Single-instance (this deployment) is unchanged.
- B-01 (sidecar binding): the ext-authz sidecar's default extractor reads the interaction from a
  CLIENT-CONTROLLABLE header. Run it ONLY as a standalone decision endpoint (as here), or behind an
  upstream that re-verifies the same envelope it executes. Do NOT place it inline in front of a
  body-carrying upstream until build-order step 4 (derive interaction from the ext_authz request
  body/path) is built.
