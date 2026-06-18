"""
Governance deployment shim - wire R1 (approver provenance + role) into a stock gate.

PROBLEM this solves. The gate runs `uvicorn IMPLEMENTATION.pep:app`. pep resolves
approver trust from either a STATIC env pin (ELYON_APPROVER_KEY_ID +
ELYON_APPROVER_PUBKEY_HEX) or the `_INJECTED_APPROVER_KEYS` seam. The STATIC pin
has NO provenance and NO role - it is exactly the [FIX H5] weakness R1 closes.
This module is the thin ASGI entrypoint that wires R1's load-bearing path: it
resolves the approver public keys from the SIGNED key-record chain with
ROLE-DISTINCTNESS (IMPLEMENTATION/approver_trust.resolve_approver_keys), injects
the result into pep, and re-exposes pep's app. Run the gate as:

    uvicorn deploy.governance.approver_trust_bootstrap:app --host 0.0.0.0 --port 8000

Env contract (see deploy/governance.env.example):
  ELYON_APPROVER_KEY_RECORD_PATH  - path to the publisher-SIGNED key record (JSON)
                                    that carries the approver-role key (and may
                                    carry the gate's issuer-role key too).
  ELYON_PINNED_ROOT_KEY_ID        - the root_key_id this gate pins out-of-band.
  ELYON_PINNED_ROOT_PUBKEY_B64    - base64(raw Ed25519) of that pinned root key.
  ELYON_SIGNING_KEY_ID            - the gate's issuer key id; passed as gate_key_id
                                    so the resolver excludes it (belt-and-braces).
  ELYON_CLOCK_SKEW_SECONDS        - optional; cross-host skew for the key window.

Fail-closed: if the record is missing/invalid, the pinned root does not verify it,
or NO key in it carries the signed role "approver", the injected map is EMPTY -
every grant is then REF_APPROVAL_KEY_UNKNOWN (no approval is honored). Custody
([FIX H5]) is NOT this module's job and MUST hold in the deployment: the approver
PRIVATE key lives only in the separate approver-CLI process (ELYON_APPROVER_KEY_HEX
there), NEVER on the gate host. This shim only ever handles PUBLIC keys.
"""

import base64
import os
from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import IMPLEMENTATION.pep as pep
from IMPLEMENTATION.key_record_source import load_key_record_from_bytes
from IMPLEMENTATION.approver_trust import resolve_approver_keys


def _pinned_root_keys():
    root_id = os.environ.get("ELYON_PINNED_ROOT_KEY_ID")
    root_b64 = os.environ.get("ELYON_PINNED_ROOT_PUBKEY_B64")
    if not root_id or not root_b64:
        return None
    raw = base64.b64decode(root_b64, validate=True)
    return {root_id: Ed25519PublicKey.from_public_bytes(raw)}


def resolve_injected_approver_keys():
    """Load the signed key record, validate it against the pinned root, and
    resolve the role-distinct approver public-key map. Returns {} (fail-closed)
    on any missing/invalid input rather than raising into app startup."""
    record_path = os.environ.get("ELYON_APPROVER_KEY_RECORD_PATH")
    pinned = _pinned_root_keys()
    gate_key_id = os.environ.get("ELYON_SIGNING_KEY_ID")
    if not record_path or pinned is None:
        return {}
    try:
        with open(record_path, "rb") as fh:
            record_bytes = fh.read()
    except OSError:
        return {}
    skew_s = os.environ.get("ELYON_CLOCK_SKEW_SECONDS")
    skew = timedelta(seconds=int(skew_s)) if skew_s else timedelta(0)
    loaded = load_key_record_from_bytes(record_bytes, pinned, clock_skew=skew)
    if loaded.get("trust_view") is None:
        return {}
    return resolve_approver_keys(
        loaded["trust_view"], gate_key_id=gate_key_id, clock_skew=skew
    )


# Wire at import (startup): resolve role-distinct approver keys and inject them so
# pep.verify_grant trusts ONLY signed "approver"-role keys, then re-export the app.
pep._INJECTED_APPROVER_KEYS = resolve_injected_approver_keys()
app = pep.app
