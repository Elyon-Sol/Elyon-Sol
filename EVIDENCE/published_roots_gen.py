"""
Live generator for the B-prime-3 published signed root record (VL-044,
T-root-recovery). Repo path: EVIDENCE/published_roots_gen.py.

Parallel to EVIDENCE/published_keys_gen.py (the B-prime-2 key-record generator),
one trust layer up: it builds the root/succession record DICT from a declared set
of roots (each with status active/retired/revoked and an optional successor
designation), signs it with a publisher/ROOT private key, and writes
EVIDENCE/published_roots.json as ASCII JSON (ensure_ascii=True, VL-009).

Per constraint (i): the record is derived LIVE here and never hand-copied.
Per the trust model (11_root_record_spec.md sections 4, 6): only the
publisher_signature is excluded from the signed region, so serial, the record
not_after, and every root entry (its status, window, retired_at/revoked_at, and
successor_of) are covered by the signature - an adversary cannot extend a window,
flip a status, roll the serial back, or swap a successor's key bytes without
breaking it.

The root PRIVATE key is NEVER persisted to the repo. build_root_record() takes a
duck-typed signing root object (.sign); the __main__ demo generates EPHEMERAL live
root keypairs (R1 active, R2 designated successor), writes a sample record, and
prints R1's PUBLIC key (base64) so a target can pin it out-of-band. The reader pins
the root PUBLIC key (root_record_source.pinned_root_keys), never the private half.

canonical_json is REUSED from envelope.py (not reimplemented) so the gen-side and
reader-side canonicalization are identical - a mismatch would make every signature
fail to verify. Imported with the IMPLEMENTATION. prefix per the VL-027
import-convention finding. INTEGRATION CHECK: run an import test in the real
environment (python -c "import EVIDENCE.published_roots_gen") before trusting this
module, per VL-027 (an unseen import surfaces only at runtime).
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
# Prefix-ful import per VL-027.
from IMPLEMENTATION.envelope import canonical_json

ROOT_RECORD_FORMAT = "elyon-sol-root-record"
ROOT_RECORD_VERSION = 1
_VALID_STATUSES = ("active", "retired", "revoked")

# The single field excluded from the signed region (everything else is signed).
_SIGNATURE_FIELD = "publisher_signature"


def public_key_b64(public_key: Ed25519PublicKey) -> str:
    """Base64 of the raw 32-byte Ed25519 public key (the on-the-wire form)."""
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def make_root_entry(
    root_key_id: str,
    public_key: Ed25519PublicKey,
    status: str,
    not_before: datetime,
    not_after: datetime,
    retired_at: Optional[datetime] = None,
    revoked_at: Optional[datetime] = None,
    successor_of: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build one root entry. not_before / not_after are the ROOT's lifecycle window.
    Timestamps must be tz-aware; the reader treats naive/unparseable timestamps as
    fail-closed. A `retired` entry MUST carry retired_at; a `revoked` entry MUST
    carry revoked_at (11_root_record_spec.md sections 4, 7 step 1; the reader
    enforces this and the generator will not silently omit them).
    """
    if status not in _VALID_STATUSES:
        raise ValueError("status must be one of %s" % (_VALID_STATUSES,))
    for label, dt in (("not_before", not_before), ("not_after", not_after)):
        if dt.tzinfo is None:
            raise ValueError("root entry %s must be tz-aware" % label)
    if status == "retired" and retired_at is None:
        raise ValueError("a retired root entry must carry retired_at")
    if status == "revoked" and revoked_at is None:
        raise ValueError("a revoked root entry must carry revoked_at")
    entry: Dict[str, Any] = {
        "root_key_id": root_key_id,
        "public_key": public_key_b64(public_key),
        "status": status,
        "not_before": not_before.isoformat(),
        "not_after": not_after.isoformat(),
    }
    if retired_at is not None:
        if retired_at.tzinfo is None:
            raise ValueError("retired_at must be tz-aware")
        entry["retired_at"] = retired_at.isoformat()
    if revoked_at is not None:
        if revoked_at.tzinfo is None:
            raise ValueError("revoked_at must be tz-aware")
        entry["revoked_at"] = revoked_at.isoformat()
    if successor_of is not None:
        entry["successor_of"] = successor_of
    return entry


def build_root_record(
    signing_root_key_id: str,
    signing_root_private_key: Any,
    roots: List[Dict[str, Any]],
    serial: int,
    not_after: datetime,
    issued_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Assemble and SIGN the root record.

    The signature covers canonical_json(record minus publisher_signature), encoded
    utf-8, with ensure_ascii=True canonicalization. Returns the record dict
    including the hex publisher_signature.

    signing_root_private_key is duck-typed (.sign(bytes) -> bytes), so this module
    does not force a specific key implementation on callers (the runner/tests pass
    a live Ed25519PrivateKey; an operator could pass an HSM-backed object). It is
    the private half of the root pinned out-of-band as signing_root_key_id.
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
        "format": ROOT_RECORD_FORMAT,
        "version": ROOT_RECORD_VERSION,
        "signing_root_key_id": signing_root_key_id,
        "serial": serial,
        "issued_at": issued_at.isoformat(),
        "not_after": not_after.isoformat(),
        "roots": list(roots),
    }
    message = canonical_json(record).encode("utf-8")
    signature = signing_root_private_key.sign(message)
    record[_SIGNATURE_FIELD] = signature.hex()
    return record


def write_root_record(path: str, record: Dict[str, Any]) -> None:
    """Write the record as ASCII JSON (VL-009). Trailing newline for POSIX."""
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True,
                                indent=2))
        handle.write("\n")


def _demo() -> int:
    """
    Operator/runner demo: generate LIVE ephemeral root keypairs and write a sample
    record in which R1 (active, the signer) DESIGNATES R2 (active, successor_of R1).
    Print R1's PUBLIC key (base64) for out-of-band pinning. The root private keys
    are never persisted. This is the planned-rotation seed: a target that pins only
    R1 can come to trust R2 from this record.
    """
    now = datetime.now(timezone.utc)
    from datetime import timedelta

    r1_private = Ed25519PrivateKey.generate()
    r2_private = Ed25519PrivateKey.generate()
    r1_id, r2_id = "root-1", "root-2"

    roots = [
        make_root_entry(r1_id, r1_private.public_key(), status="active",
                        not_before=now - timedelta(days=1),
                        not_after=now + timedelta(days=365)),
        make_root_entry(r2_id, r2_private.public_key(), status="active",
                        not_before=now - timedelta(minutes=1),
                        not_after=now + timedelta(days=365),
                        successor_of=r1_id),
    ]
    record = build_root_record(
        signing_root_key_id=r1_id,
        signing_root_private_key=r1_private,
        roots=roots,
        serial=1,
        not_after=now + timedelta(hours=24),
    )
    write_root_record("published_roots.json", record)
    print("wrote published_roots.json (serial=1; R1 active, designates R2)")
    print("pin this root public key out-of-band (%s):" % r1_id)
    print("  " + public_key_b64(r1_private.public_key()))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
