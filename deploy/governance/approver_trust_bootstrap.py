"""Governance deployment entrypoint - R1 approver trust (now resolved IN pep).

HISTORY / GL-01-refine (VL-124). This module used to RESOLVE the signed key-record
chain and INJECT the resulting approver map into pep (`pep._INJECTED_APPROVER_KEYS
= resolve(...)`). That made provenance a property of the SHIM, not of the gate:
pep could not tell a shim-resolved map from any other injected map, so the startup
guard could only check injectedness, not provenance - the exact residual the review
named (an injected gate-controlled map under a different key_id passed the guard).

pep now resolves the pinned-root signed key-record chain IN-PROCESS from the SAME
env trio (ELYON_APPROVER_KEY_RECORD_PATH + ELYON_PINNED_ROOT_KEY_ID +
ELYON_PINNED_ROOT_PUBKEY_B64; ELYON_SIGNING_KEY_ID as the excluded gate key;
ELYON_CLOCK_SKEW_SECONDS optional) and labels the map with SIGNED_CHAIN provenance,
which the guard requires under a high-impact manifest. So this module no longer
injects anything - it is a thin, back-compatible entrypoint that re-exports pep's
app. The env contract and the run command are UNCHANGED, so existing deploy
artifacts (docker-compose.governance.yml, GOVERNANCE_DEPLOYMENT.md) keep working:

    uvicorn deploy.governance.approver_trust_bootstrap:app --host 0.0.0.0 --port 8000

is now byte-equivalent to running `uvicorn IMPLEMENTATION.pep:app` with the trio
set. New deployments may point straight at pep; this alias remains for the
committed compose files and runbooks.

Env contract (unchanged; see deploy/governance.env.example):
  ELYON_APPROVER_KEY_RECORD_PATH  - path to the publisher-SIGNED key record (JSON)
                                    carrying the approver-role key.
  ELYON_PINNED_ROOT_KEY_ID        - the root_key_id this gate pins out-of-band.
  ELYON_PINNED_ROOT_PUBKEY_B64    - base64(raw Ed25519) of that pinned root key.
  ELYON_SIGNING_KEY_ID            - the gate issuer key id (excluded from the map).
  ELYON_CLOCK_SKEW_SECONDS        - optional; cross-host skew for the key window.

Fail-closed (in pep now): a missing/invalid record, a non-verifying pinned root,
or NO key carrying the signed role "approver" resolves to an EMPTY approver map -
every grant is then REF_APPROVAL_KEY_UNKNOWN, and a high-impact gate refuses to
start (G-06). Custody ([FIX H5]) is a DEPLOYMENT property, not this module's job:
the approver PRIVATE key lives only in the separate approver-CLI process, NEVER on
the gate host. The gate ever handles only PUBLIC keys.
"""

import IMPLEMENTATION.pep as pep

# pep resolves the signed-chain approver map natively (with SIGNED_CHAIN
# provenance) from the env trio above - no injection here. Re-export the app so
# the historical `...approver_trust_bootstrap:app` entrypoint still resolves.
app = pep.app
