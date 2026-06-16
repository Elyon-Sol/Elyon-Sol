"""Live ext-authz sidecar ALLOW/DENY check over the public surface (AUTHOR; CI-excluded).

Mints a real admissibility envelope from the gate, presents it to the authz sidecar
(X-Elyon-Sol-Envelope + X-Elyon-Sol-Interaction headers), and asserts:
  - a VALID envelope  -> ALLOW (HTTP 200)
  - a TAMPERED one    -> DENY  (HTTP 403)
Closes the live-ALLOW gap for claim 13 (the byte-anchor self-test does not cover the sidecar).

Run (from a checkout with deps; real CA so no bundle):
    ELYON_LIVE_GATE_URL=https://gate.elyon-sol.io:8443 \
    ELYON_LIVE_SIDECAR_URL=https://authz.elyon-sol.io:9243 \
    ELYON_LIVE_TARGET_ID=https://target.elyon-sol.io:9443/target \
    python -m EVIDENCE.proofs.sidecar_live_check
"""
import os, sys, requests
from IMPLEMENTATION.mcp_server import interaction_for
from IMPLEMENTATION.envelope import canonical_json
from EVIDENCE.proofs.attack_harness import TOOL, ARGS

gate = os.environ.get("ELYON_LIVE_GATE_URL")
side = os.environ.get("ELYON_LIVE_SIDECAR_URL")
target_id = os.environ.get("ELYON_LIVE_TARGET_ID")
if not (gate and side and target_id):
    print("set ELYON_LIVE_GATE_URL, ELYON_LIVE_SIDECAR_URL, ELYON_LIVE_TARGET_ID"); sys.exit(2)

def elyon_headers(resp):
    return {k: v for k, v in resp.headers.items() if "elyon" in k.lower()}

print("=" * 88)
print("LIVE SIDECAR ALLOW/DENY CHECK (claim 13) -", side)
print("=" * 88)

inter = interaction_for(TOOL, ARGS)
r = requests.post(gate + "/governed-call",
                  json={"target_url": target_id, "interaction": inter}, timeout=20)
if r.status_code != 200 or "envelope" not in r.json():
    print("[FAIL] mint via gate failed:", r.status_code, r.text[:300]); sys.exit(1)
env = r.json()["envelope"]

allow = requests.post(side + "/authz",
                      headers={"X-Elyon-Sol-Envelope": canonical_json(env),
                               "X-Elyon-Sol-Interaction": canonical_json(inter)}, timeout=20)
print("[ALLOW] valid envelope ->", allow.status_code, elyon_headers(allow))

forged = dict(env); forged["decision_id"] = "forged-" + str(forged.get("decision_id"))
deny = requests.post(side + "/authz",
                     headers={"X-Elyon-Sol-Envelope": canonical_json(forged),
                              "X-Elyon-Sol-Interaction": canonical_json(inter)}, timeout=20)
print("[DENY]  tampered envelope ->", deny.status_code, elyon_headers(deny))

ok = (allow.status_code == 200) and (deny.status_code == 403)
print("-" * 88)
print("RESULT:", "PASS - sidecar ALLOWs valid, DENYs tampered" if ok
      else "FAIL - investigate before exposure")
sys.exit(0 if ok else 1)
