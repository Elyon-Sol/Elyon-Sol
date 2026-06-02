"""
Live generator for the B-prime-2 published signed key record (VL-042,
T-key-record). Repo path: EVIDENCE/published_keys_gen.py.

Parallel to EVIDENCE/published_hashes_gen.py (the B-prime-1 hash-record
generator): it builds the published key record DICT from a declared set of
issuer keys, signs it with the publisher/ROOT private key, and writes
EVIDENCE/published_keys.json as ASCII JSON (ensure_ascii=True, VL-009).

Per constraint (i): the record is derived LIVE here and never hand-copied.
Per the trust model (09_key_record_spec.md sections 4, 6): only the
publisher_signature is excluded from the signed region, so serial, the
record not_after, and every key entry (including its revoked flag and window)
are covered by the signature - an adversary cannot extend the window,
un-revoke a key, roll the serial back, or swap key bytes without breaking it.

The root PRIVATE key is NEVER persisted to the repo. build_key_record()
takes a duck-typed root signing object (.sign); the __main__ demo generates
an EPHEMERAL live root keypair, writes a sample record, and prints the root
PUBLIC key (base64) so a target can pin it out-of-band. The reader pins the
root PUBLIC key (key_record_source.pinned_root_keys), never the private half.

canonical_json is REUSED from envelope.py (not reimplemented) so the
gen-side and reader-side canonicalization are identical - a mismatch would
make every signature fail to verify. Imported with the IMPLEMENTATION.
prefix per the VL-027 import-convention finding. INTEGRATION CHECK: run an
import test in the real environment (python -c "import
EVIDENCE.published_keys_gen") before trusting this module, per VL-027
(an unseen import surfaces only at runtime).
"""

import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# Reuse the SAME canonicalization the verifier/signer use (ensure_ascii=True).
# See module docstring: prefix-ful import per VL-027; reconcile the name with
# envelope.py at integration if it differs.
from IMPLEMENTATION.envelope import canonical_json

KEY_RECORD_FORMAT = "elyon-sol-key-record"
KEY_RECORD_VERSION = 1

# The single field excluded from the signed region (everything else is signed).
_SIGNATURE_FIELD = "publisher_signature"


def public_key_b64(public_key: Ed25519PublicKey) -> str:
    """Base64 of the raw 32-byte Ed25519 public key (the on-the-wire form)."""
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def make_key_entry(
    key_id: str,
    public_key: Ed25519PublicKey,
    not_before: datetime,
    not_after: datetime,
    revoked: bool = False,
    revoked_at: Optional[datetime] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build one issuer-key entry. not_before / not_after are the KEY's lifecycle
    window (distinct from an envelope's own not_after, VL-041). Timestamps must
    be tz-aware; the reader treats naive/unparseable timestamps as fail-closed.
    """
    for label, dt in (("not_before", not_before), ("not_after", not_after)):
        if dt.tzinfo is None:
            raise ValueError("key entry %s must be tz-aware" % label)
    entry: Dict[str, Any] = {
        "key_id": key_id,
        "public_key": public_key_b64(public_key),
        "not_before": not_before.isoformat(),
        "not_after": not_after.isoformat(),
        "revoked": bool(revoked),
    }
    if revoked:
        if revoked_at is not None:
            if revoked_at.tzinfo is None:
                raise ValueError("revoked_at must be tz-aware")
            entry["revoked_at"] = revoked_at.isoformat()
        if reason is not None:
            entry["reason"] = reason
    return entry


def build_key_record(
    root_key_id: str,
    root_private_key: Any,
    keys: List[Dict[str, Any]],
    serial: int,
    not_after: datetime,
    issued_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Assemble and SIGN the key record.

    The signature covers canonical_json(record minus publisher_signature),
    encoded utf-8, with ensure_ascii=True canonicalization. Returns the record
    dict including the hex publisher_signature.

    root_private_key is duck-typed (.sign(bytes) -> bytes), so this module does
    not force a specific key implementation on callers (the runner/tests pass a
    live Ed25519PrivateKey; an operator could pass an HSM-backed object).
    """
    if not isinstance(serial, int) or isinstance(serial, bool) or serial < 0:
        raise ValueError("serial must be a non-negative integer")
    if not_after.tzinfo is None:
        raise ValueError("record not_after must be tz-aware")
    if issued_at is None:
        issued_at = datetime.now(timezone.utc)
    if issued_at.tzinfo is None:
        raise ValueError("issued_at must be tz-aware")

    record: Dict[str, Any] = {
        "format": KEY_RECORD_FORMAT,
        "version": KEY_RECORD_VERSION,
        "root_key_id": root_key_id,
        "serial": serial,
        "issued_at": issued_at.isoformat(),
        "not_after": not_after.isoformat(),
        "keys": list(keys),
    }
    message = canonical_json(record).encode("utf-8")
    signature = root_private_key.sign(message)
    record[_SIGNATURE_FIELD] = signature.hex()
    return record


def write_key_record(path: str, record: Dict[str, Any]) -> None:
    """Write the record as ASCII JSON (VL-009). Trailing newline for POSIX."""
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True,
                                indent=2))
        handle.write("\n")


def _demo() -> int:
    """
    Operator/runner demo: generate a LIVE ephemeral root keypair, build a
    sample record with one valid and one revoked issuer key, write it, and
    print the root PUBLIC key (base64) for out-of-band pinning. The root
    private key is never persisted.
    """
    now = datetime.now(timezone.utc)
    root_private = Ed25519PrivateKey.generate()
    root_id = "root-demo-1"

    issuer_a = Ed25519PrivateKey.generate().public_key()
    issuer_b = Ed25519PrivateKey.generate().public_key()
    from datetime import timedelta
    keys = [
        make_key_entry("issuer-a", issuer_a,
                       not_before=now - timedelta(days=1),
                       not_after=now + timedelta(days=365)),
        make_key_entry("issuer-b", issuer_b,
                       not_before=now - timedelta(days=30),
                       not_after=now + timedelta(days=365),
                       revoked=True, revoked_at=now,
                       reason="demo: compromised key"),
    ]
    record = build_key_record(
        root_key_id=root_id,
        root_private_key=root_private,
        keys=keys,
        serial=1,
        not_after=now + timedelta(hours=24),
    )
    write_key_record("published_keys.json", record)
    print("wrote published_keys.json (serial=1)")
    print("pin this root public key out-of-band (%s):" % root_id)
    print("  " + public_key_b64(root_private.public_key()))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
