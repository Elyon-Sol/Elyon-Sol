# Manual test: the ext-authz sidecar over real TLS on your two VMs (VL-105)

A step-by-step to stand up `elyon-authz` (the admissibility sidecar) under real TLS
on your existing two-VM cross-host setup and confirm ALLOW/DENY over HTTPS with a
real gate-minted envelope. Companion to `deploy/host_setup_virtualbox.md` (the VM
provisioning), `deploy/tls/trust_bootstrap.md` (trust material), and
`deploy/elyon-authz/README.md` (the sidecar itself).

**Honest scope.** Two VMs are distinct OS hosts with a real network + real TLS, so
this exercises the sidecar over real cross-host transport. It is NOT the
public-internet / external-attacker referent (both ends are under your control) - so
it does not move G5. It proves the sidecar's decision path is unchanged over TLS.

The in-sandbox equivalents (run them first to know the artifacts are good):

```
# hermetic, CI-safe: the elyon-authz TLS leaf establishes a verified session
python -m pytest TESTS/deploy/test_authz_sidecar_tls.py -v

# real loopback TLS: the sidecar answers ALLOW/DENY over HTTPS verifying the CA
PYTHONPATH=. python3 EVIDENCE/proofs/authz_sidecar_tls_001_runner.py
```

---

## Topology

Reuse the `host_setup_virtualbox.md` split, with the sidecar added on VM-B:

| Host | Runs | Ports |
| --- | --- | --- |
| VM-A `192.168.56.101` | gate (`pep`) | 8000 (TLS) |
| VM-B `192.168.56.102` | target, publisher, **elyon-authz** | 9000 / 9100 / **9200** (TLS) |

The sidecar sits on VM-B in front of the target; it answers "is this admissible?"
for envelopes the VM-A gate minted. (The Envoy+OPA Mode A chain is optional - see
the last section; the core test below is the sidecar directly over HTTPS.)

---

## 1. Generate certs with your real hostnames (VM-B, then ship the CA)

The `elyon-authz` leaf now ships in `gen_certs.py`. Include VM-B's hostname/IP as an
extra SAN so a client addressing VM-B verifies the cert:

```
# on VM-B, in the repo root
python deploy/tls/gen_certs.py 192.168.56.102 vm-b.internal
#   -> deploy/tls/certs/ : ca.crt + {gate,target,publisher,elyon-authz}.{crt,key}
```

Ship `ca.crt` out-of-band to whichever host runs the test client (VM-A or your
host). Keep `elyon-authz.key` only on VM-B. (Public-CA path: see
`trust_bootstrap.md` Path B and leave `ELYON_TLS_CA_BUNDLE` unset.)

## 2. Bootstrap the trust material (gate key + anchor)

```
cd deploy && python bootstrap_config.py      # writes deploy/.env
grep -E "ELYON_GATE_KEY_ID|ELYON_GATE_PUBLIC_KEY_HEX|ELYON_PINNED_ROOT_SHA256" .env
```

These three values are the sidecar's out-of-band trust base (same ones the
reference target uses). The gate public key must match the gate's signing key on
VM-A (`bootstrap_config.py` generates the pair; the private half stays on VM-A).

## 3. Stand up the sidecar on VM-B under TLS

Either bare uvicorn (simplest for a direct test) or the compose overlay.

**Bare uvicorn (VM-B):**

```
export ELYON_TARGET_URL="https://192.168.56.102:9000/target"   # the identity envelopes bind to
export ELYON_RECORD_PATH="EVIDENCE/published_hashes.json"
export ELYON_PINNED_ROOT_SHA256="<from .env>"
export ELYON_GATE_KEY_ID="<from .env>"
export ELYON_GATE_PUBLIC_KEY_HEX="<from .env>"
# optional, if VM clocks drift: export ELYON_CLOCK_SKEW_SECONDS=5

uvicorn IMPLEMENTATION.authz_sidecar:app --host 0.0.0.0 --port 9200 \
  --ssl-certfile deploy/tls/certs/elyon-authz.crt \
  --ssl-keyfile  deploy/tls/certs/elyon-authz.key
```

`ELYON_TARGET_URL` must equal the `target_url` the gate admits against (what the
client passes to `/governed-call`). Any required env var missing -> the sidecar
answers every request `403 REF_TARGET_NOT_CONFIGURED` (fail closed).

**Compose overlay (VM-B):**

```
cd deploy && docker compose \
  -f docker-compose.yml \
  -f docker-compose.authz.yml \
  -f docker-compose.authz.tls.yml \
  up --build elyon-authz
```

Liveness: `curl --cacert deploy/tls/certs/ca.crt https://192.168.56.102:9200/healthz`
-> `{"status":"ok"}`.

## 4. Mint a real envelope from VM-A's gate, present it to VM-B's sidecar

Run this client from a host that trusts `ca.crt` (set `CA` to its path). It asks
VM-A's gate for an envelope, then presents it to VM-B's sidecar over HTTPS:

```python
# present_to_sidecar.py  -- run from the repo root; needs httpx + the repo importable
import json, os, httpx
from IMPLEMENTATION.envelope import canonical_json
from IMPLEMENTATION.mcp_server import interaction_for

GATE    = os.environ["GATE"]      # https://192.168.56.101:8000
SIDECAR = os.environ["SIDECAR"]   # https://192.168.56.102:9200
CA      = os.environ["CA"]        # path to ca.crt
TARGET  = os.environ["TARGET"]    # must equal ELYON_TARGET_URL on the sidecar
c = httpx.Client(verify=CA, trust_env=False, timeout=10.0)

args = {"amount": 100, "to": "acct-42"}
interaction = interaction_for("transfer_funds", args)

# 1) mint: the gate returns the signed envelope in its response
env = c.post(f"{GATE}/governed-call",
             json={"target_url": TARGET, "interaction": interaction}).json()["envelope"]

# 2) present to the sidecar (the two headers the default extractor reads)
def ask(envelope, inter):
    r = c.post(f"{SIDECAR}/authz", headers={
        "X-Elyon-Sol-Envelope": canonical_json(envelope),
        "X-Elyon-Sol-Interaction": canonical_json(inter),
    })
    return r.status_code, r.headers.get("x-elyon-decision"), r.headers.get("x-elyon-reason")

print("ALLOW   ", ask(env, interaction))                       # -> 200 ALLOW
bad = {**env, "request_context": {**env["request_context"],
       "AP": env["request_context"]["AP"] + ["smuggled"]}}
print("FORGED  ", ask(bad, interaction))                       # -> 403 ... SIGNATURE_INVALID
print("REBIND  ", ask(env, interaction_for("delete_database", {"db": "prod"})))  # -> 403 BINDING_MISMATCH
print("REPLAY  ", ask(env, interaction))                       # -> 403 REPLAY (env already honored above)
```

```
GATE=https://192.168.56.101:8000 SIDECAR=https://192.168.56.102:9200 \
CA=deploy/tls/certs/ca.crt TARGET=https://192.168.56.102:9000/target \
python present_to_sidecar.py
```

Expected:

```
ALLOW    (200, 'ALLOW', 'REASSERTED_AND_BOUND')
FORGED   (403, 'DENY', 'REF_VERIFY_SIGNATURE_INVALID')
REBIND   (403, 'DENY', 'REF_VERIFY_BINDING_MISMATCH')
REPLAY   (403, 'DENY', 'REF_VERIFY_REPLAY')
```

Un-attested check (no envelope header) from the shell:

```
curl -s -o /dev/null -w "%{http_code} %header{x-elyon-reason}\n" \
  --cacert deploy/tls/certs/ca.crt -X POST https://192.168.56.102:9200/authz
#   -> 403 REF_VERIFY_ENVELOPE_ABSENT
```

## 5. (Optional) the full Envoy Mode A chain over TLS

To test the two-filter chain (elyon-authz then OPA) in front of the target:

1. Bring up `docker-compose.yml` + `docker-compose.authz.yml` + the TLS overlays.
2. Give Envoy's `elyon_authz` cluster an upstream TLS context (the snippet at the
   bottom of `docker-compose.authz.tls.yml`) so Envoy verifies the sidecar leaf
   under `ca.crt`, and switch the `http_service` server_uri to https.
3. `envoy --mode validate -c deploy/envoy.example.yaml` before `up`.
4. Hit Envoy's public listener (`:10000`) with the attestation headers; admissibility
   (sidecar) is enforced before policy (OPA).

## Troubleshooting

- `REF_TARGET_NOT_CONFIGURED` on every call: a required `ELYON_*` env var is unset,
  the record file path is wrong, or the gate public key is malformed. The sidecar
  fails closed per request rather than booting unconfigured.
- TLS verify error / hostname mismatch: the client must address VM-B by a name in
  the leaf SAN (the IP/hostname you passed to `gen_certs.py`), and must trust
  `ca.crt`. `--cacert` (curl) / `verify=CA` (httpx).
- `REF_VERIFY_BINDING_MISMATCH` on a request you expected to pass: `ELYON_TARGET_URL`
  on the sidecar must exactly equal the `target_url` the gate admitted against.
- `REF_VERIFY_SIGNATURE_EXPIRED` with healthy clocks: the decision aged out
  (default 300s on the gate); mint fresh. Genuine VM clock drift: set
  `ELYON_CLOCK_SKEW_SECONDS`.

## What this proves / does not

Proves: the sidecar enforces admissibility unchanged over real cross-host TLS - a
valid attested request is honored, and forged / rebound / replayed / un-attested
requests are refused with the existing REF_* reasons. Does not: stand in for an
external attacker on a public surface (G5 / GR-3) - both ends here are yours.
