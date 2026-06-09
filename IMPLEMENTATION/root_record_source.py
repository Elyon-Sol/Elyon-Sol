"""
B-prime-3 root-record reader for Elyon-Sol (VL-044, T-root-recovery). Repo path:
IMPLEMENTATION/root_record_source.py.

MIRRORS IMPLEMENTATION/key_record_source.py (the B-prime-2 key-record reader) as a
SIBLING module, not an extension (11_root_record_spec.md sections 7, 15). It shares
the SAME trust primitive as B-prime-2 (a pinned root PUBLIC KEY plus a verified
publisher signature, so the record may change under a stable pin), the same import
profile (it reconstructs root public keys, so it imports cryptography, keeping
verifier.py / envelope.py import-clean), and the same INVALID/STALE discriminating
return contract. It is a sibling rather than an extension because what it vouches
for (ROOTS) and its threat surface (succession authority, retired-vs-revoked, the
bootstrap floor) are distinct from the issuer-key reader's.

Three layers, mirroring key_record_source.py:
  load_root_record_from_bytes() - the pure, network-free trust check (verify
      publisher signature -> freshness -> bootstrap downgrade -> within-record
      consistency -> build the per-root STATUS VIEW). now is injectable.
  fetch_root_record()           - the transport: requests.get over loopback, then
      load_root_record_from_bytes. The only network-touching layer; fail-closed on
      any connection / non-200 / timeout.

The pinned root, like B-prime-1's and B-prime-2's pinned anchor, is held
OUT-OF-BAND and is NEVER fetched alongside the record (that would be circular).

This reader resolves a per-root STATUS VIEW only; it does NOT touch envelopes. The
status view is consumed one layer down by key_record_source.load_key_record_from_bytes
(its new root_status_view parameter), which uses it to refuse a key record whose
SIGNING root is retired-for-a-new-record or revoked. verify_envelope is unchanged
(11_root_record_spec.md section 8).

CROSS-SIGNER overlap conflict (two trusted roots asserting contradictory status in
two DIFFERENT records) is NOT a function of this single-record loader - it sees one
signer. That is a named deployment-layer hazard resolved by out-of-band re-pin
(spec section 6.3). What this loader DOES enforce is the WITHIN-record analog: a
root_key_id appearing more than once in one record's roots[] is malformed.

REF_VERIFY_ROOT_RECORD_* codes: verifier.py is the canonical home of the full
REF_VERIFY_* namespace. This reader EMITS the two record-level codes
(REF_VERIFY_ROOT_RECORD_INVALID, REF_VERIFY_ROOT_RECORD_STALE) and IMPORTS them from
verifier.py for a single source of truth. The two key-record-level root codes
(REF_VERIFY_ROOT_RETIRED, REF_VERIFY_ROOT_REVOKED) are decided in
key_record_source's cross-record gate, not here. No cycle: verifier imports
envelope, not this module. INTEGRATION ORDER: apply the verifier.py VL-044 edits
(which add these codes) before placing this reader.
"""

import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# REF_VERIFY_ROOT_RECORD_* are defined canonically in verifier.py (the
# REF_VERIFY_* home). The reader EMITS these two and imports them so there is a
# single source of truth.
from IMPLEMENTATION.verifier import (
    REF_VERIFY_ROOT_RECORD_INVALID,
    REF_VERIFY_ROOT_RECORD_STALE,
)

# canonical_json is REUSED from envelope.py so reader-side canonicalization matches
# the gen/sign side exactly (prefix-ful import per VL-027). INTEGRATION CHECK:
# verify this import resolves in the real environment before trusting the module.
from IMPLEMENTATION.envelope import canonical_json

ROOT_RECORD_FORMAT = "elyon-sol-root-record"
_SIGNATURE_FIELD = "publisher_signature"
_VALID_STATUSES = frozenset({"active", "retired", "revoked"})
_REQUIRED_RECORD_KEYS = (
    "format", "version", "signing_root_key_id", "serial",
    "issued_at", "not_after", "roots", _SIGNATURE_FIELD,
)
_REQUIRED_ROOT_FIELDS = ("root_key_id", "public_key", "status",
                         "not_before", "not_after")


def _reject(reason: str) -> Dict[str, Any]:
    return {"status_view": None, "reason": reason}


def _parse_aware(value: Any) -> datetime:
    """
    Parse an ISO-8601 timestamp to a tz-AWARE datetime. Raises ValueError on a
    non-string, an unparseable string, or a tz-naive result. Accepts a trailing
    Z by normalizing to +00:00.
    """
    if not isinstance(value, str):
        raise ValueError("timestamp not a string")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(text)  # raises ValueError on bad format
    if dt.tzinfo is None:
        raise ValueError("timestamp is tz-naive")
    return dt


def _structurally_valid(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    for key in _REQUIRED_RECORD_KEYS:
        if key not in record:
            return False
    if record.get("format") != ROOT_RECORD_FORMAT:
        return False
    if not isinstance(record.get("signing_root_key_id"), str):
        return False
    if not isinstance(record.get("serial"), int) or isinstance(
        record.get("serial"), bool
    ):
        return False
    if not isinstance(record.get("publisher_signature"), str):
        return False
    if not isinstance(record.get("roots"), list):
        return False
    return True


def load_root_record_from_bytes(
    record_bytes: bytes,
    pinned_root_keys: Dict[str, Any],
    now: Optional[datetime] = None,
    last_seen_root_serial: Optional[int] = None,
    clock_skew: timedelta = timedelta(0),
) -> Dict[str, Any]:
    """
    The pure, network-free trust check. Returns
    {"status_view": <dict>, "reason": None} on success, or
    {"status_view": None, "reason": <REF_VERIFY_ROOT_RECORD_*>} on any fault.

    Order (each step fail-closed, 11_root_record_spec.md section 7):
      1. parse JSON + structural validation         -> RECORD_INVALID
      2. select pinned signing root by signing_root_key_id -> RECORD_INVALID
      3. verify publisher_signature vs pinned root   -> RECORD_INVALID
      4. freshness: now < not_after + clock_skew;
         serial monotonic if last_seen given         -> RECORD_STALE
      5. bootstrap downgrade: a self-`revoked` assertion on the signing root is
         treated as at-most `retired` (spec section 6.2); the self-revocation
         timestamp becomes the effective retired_at.
      6. within-record consistency: a root_key_id appearing more than once in
         roots[] is malformed                        -> RECORD_INVALID
      7. build per-root STATUS VIEW (reconstruct keys, parse windows, enforce
         status-conditional timestamps)              -> RECORD_INVALID on faults

    The status view (spec section 7 step 7):
        {root_key_id: {"public_key": <obj>, "status": <str>,
                       "not_before": <aware dt>, "not_after": <aware dt>,
                       "retired_at": <aware dt|None>, "revoked_at": <aware dt|None>}}

    clock_skew (VL-075, B2; spec 15_clock_skew_tolerance_spec.md): a non-negative
    tolerance for cross-host clock divergence. The RECORD-level freshness check
    becomes now < not_after + clock_skew (default timedelta(0) -> the strict
    pre-VL-075 check). The per-root validity windows in the status view are stored
    raw. A negative value narrows the window (a config error) and raises ValueError.
    """
    if clock_skew < timedelta(0):
        raise ValueError("clock_skew must be non-negative")
    if now is None:
        now = datetime.now(timezone.utc)
    if not isinstance(pinned_root_keys, dict) or not pinned_root_keys:
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)

    # 1. parse + structure
    try:
        record = json.loads(record_bytes)
    except (json.JSONDecodeError, ValueError):
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
    if not _structurally_valid(record):
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)

    # 2. select pinned signing root (unknown signing root cannot validate; folded)
    signing_root_id = record["signing_root_key_id"]
    root_key = pinned_root_keys.get(signing_root_id)
    if root_key is None:
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)

    # 3. publisher signature over canonical_json(record minus signature)
    unsigned = {k: v for k, v in record.items() if k != _SIGNATURE_FIELD}
    try:
        signature = bytes.fromhex(record[_SIGNATURE_FIELD])
    except (ValueError, TypeError):
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
    message = canonical_json(unsigned).encode("utf-8")
    try:
        root_key.verify(signature, message)
    except InvalidSignature:
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
    except Exception:
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)

    # 4. freshness: record not_after, then serial rollback if state persisted
    try:
        record_not_after = _parse_aware(record["not_after"])
    except ValueError:
        # tz-naive / unparseable not_after fails closed to STALE (spec section 5
        # freshness ownership of the field; cannot safely compare).
        return _reject(REF_VERIFY_ROOT_RECORD_STALE)
    if not (now < record_not_after + clock_skew):
        return _reject(REF_VERIFY_ROOT_RECORD_STALE)
    if last_seen_root_serial is not None and record["serial"] < last_seen_root_serial:
        return _reject(REF_VERIFY_ROOT_RECORD_STALE)

    # 6. within-record consistency: a duplicate root_key_id is malformed. (Done
    # before the view build so a dict keyed by root_key_id cannot silently dedupe
    # a contradiction. Step 5 bootstrap downgrade is applied per-entry below.)
    seen_ids = set()
    for entry in record["roots"]:
        if not isinstance(entry, dict) or "root_key_id" not in entry:
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        rid = entry["root_key_id"]
        if not isinstance(rid, str):
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        if rid in seen_ids:
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        seen_ids.add(rid)

    # 5 + 7. build the per-root status view
    status_view: Dict[str, Dict[str, Any]] = {}
    for entry in record["roots"]:
        for field in _REQUIRED_ROOT_FIELDS:
            if field not in entry:
                return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        rid = entry["root_key_id"]
        status = entry["status"]
        if status not in _VALID_STATUSES:
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        # status-conditional timestamps (spec section 4 / 7 step 1)
        if status == "retired" and "retired_at" not in entry:
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        if status == "revoked" and "revoked_at" not in entry:
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        try:
            raw = base64.b64decode(entry["public_key"], validate=True)
            public_key = Ed25519PublicKey.from_public_bytes(raw)
            not_before = _parse_aware(entry["not_before"])
            not_after = _parse_aware(entry["not_after"])
            retired_at = (_parse_aware(entry["retired_at"])
                          if "retired_at" in entry else None)
            revoked_at = (_parse_aware(entry["revoked_at"])
                          if "revoked_at" in entry else None)
        except (ValueError, TypeError, base64.binascii.Error):
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
        except Exception:
            return _reject(REF_VERIFY_ROOT_RECORD_INVALID)

        # 5. bootstrap downgrade: the signing root cannot revoke ITSELF in-band
        # (spec section 6.2). A self-`revoked` assertion is treated as at-most
        # `retired`; the self-revocation time becomes the effective retired_at so
        # the downstream retirement gate (issued_at < retired_at) has a timestamp.
        if rid == signing_root_id and status == "revoked":
            status = "retired"
            retired_at = revoked_at

        status_view[rid] = {
            "public_key": public_key,
            "status": status,
            "not_before": not_before,
            "not_after": not_after,
            "retired_at": retired_at,
            "revoked_at": revoked_at,
        }

    return {"status_view": status_view, "reason": None}


def fetch_root_record(
    publisher_url: str,
    pinned_root_keys: Dict[str, Any],
    now: Optional[datetime] = None,
    last_seen_root_serial: Optional[int] = None,
    timeout: int = 10,
    clock_skew: timedelta = timedelta(0),
) -> Dict[str, Any]:
    """
    Fetch the root record over HTTP, then run the pure trust check.

    Cross-host is modeled with loopback (the B-prime-1/2 transport model; true
    multi-machine + TLS is G5 / deployment). Any transport failure (connection,
    non-200, timeout) fails closed to RECORD_INVALID - the target refuses rather
    than proceeding without a validated record (canon section 9). The bytes are not
    trusted until the publisher signature verifies against the pinned root the
    target holds out-of-band.
    """
    try:
        response = requests.get(publisher_url, timeout=timeout)
    except Exception:
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
    if response.status_code != 200:
        return _reject(REF_VERIFY_ROOT_RECORD_INVALID)
    return load_root_record_from_bytes(
        response.content, pinned_root_keys, now=now,
        last_seen_root_serial=last_seen_root_serial,
        clock_skew=clock_skew,
    )
