"""
Live generator for the B-prime-1 SIGNED published record (VL-074, B1; the
A3b sub-case (b) record-freshness increment). Repo path:
EVIDENCE/published_hashes_signed_gen.py.

Parallel to EVIDENCE/published_keys_gen.py (the B-prime-2 key-record signer):
it wraps the three live currency pins that EVIDENCE/published_hashes_gen.py
produces (canon / evaluator / manifest sha + versions) in a SIGNED envelope
carrying a stable publisher_key_id, a monotonic serial, an issued_at, and a
not_after, signs it with the publisher private key, and (optionally) writes the
record as ASCII JSON (VL-009).

This does NOT replace EVIDENCE/published_hashes.json (the committed byte-anchor
record consumed by published_source.py and the g4/g5 runners). Build-then-wire:
the byte-anchor record and its consumers are byte-unchanged; this signer
produces the SIGNED record the new published_record_source.py reader validates.
Like the key record, the signed published record is a RUNTIME artifact: it is
re-signed (new serial + not_after) on a schedule and is NOT committed.

Per constraint (i) the currency pins are derived LIVE (from
published_hashes_gen.build_record), never hand-copied. Only publisher_signature
is excluded from the signed region, so serial, not_after, and every pin are
covered - an adversary cannot extend the window, roll the serial back, or swap a
pin without breaking the signature.

The publisher PRIVATE key is NEVER persisted to the repo. build_signed_record()
takes a duck-typed signing object (.sign); the __main__ demo generates an
EPHEMERAL live keypair, writes a sample record, and prints the publisher PUBLIC
key (base64) for out-of-band pinning. canonical_json is REUSED from envelope.py
so gen-side and reader-side canonicalization are identical.
"""

import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from IMPLEMENTATION.envelope import canonical_json
from EVIDENCE.published_hashes_gen import build_record as build_currency_pins

PUBLISHED_RECORD_FORMAT = "elyon-sol-published-record"
PUBLISHED_RECORD_VERSION = 1
_SIGNATURE_FIELD = "publisher_signature"


def public_key_b64(public_key: Any) -> str:
    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def build_signed_record(
    publisher_key_id: str,
    publisher_private_key: Any,
    serial: int,
    not_after: datetime,
    pins: Optional[Dict[str, Any]] = None,
    issued_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Assemble and SIGN the published record. The signature covers
    canonical_json(record minus publisher_signature), utf-8, ensure_ascii=True.
    pins defaults to the LIVE currency pins (published_hashes_gen.build_record).
    publisher_private_key is duck-typed (.sign(bytes) -> bytes).
    """
    if not isinstance(serial, int) or isinstance(serial, bool) or serial < 0:
        raise ValueError("serial must be a non-negative integer")
    if not_after.tzinfo is None:
        raise ValueError("record not_after must be tz-aware")
    if issued_at is None:
        issued_at = datetime.now(timezone.utc)
    if issued_at.tzinfo is None:
        raise ValueError("issued_at must be tz-aware")
    if pins is None:
        pins = build_currency_pins()

    record: Dict[str, Any] = {
        "format": PUBLISHED_RECORD_FORMAT,
        "version": PUBLISHED_RECORD_VERSION,
        "publisher_key_id": publisher_key_id,
        "serial": serial,
        "issued_at": issued_at.isoformat(),
        "not_after": not_after.isoformat(),
    }
    record.update(pins)
    message = canonical_json(record).encode("utf-8")
    record[_SIGNATURE_FIELD] = publisher_private_key.sign(message).hex()
    return record


def write_signed_record(path: str, record: Dict[str, Any]) -> None:
    """Write the record as ASCII JSON (VL-009). Trailing newline for POSIX."""
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True,
                                indent=2))
        handle.write("\n")


def _demo() -> int:
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    publisher_private = Ed25519PrivateKey.generate()
    publisher_id = "publisher-demo-1"
    record = build_signed_record(
        publisher_key_id=publisher_id,
        publisher_private_key=publisher_private,
        serial=1,
        not_after=now + timedelta(hours=24),
    )
    write_signed_record("published_hashes_signed.json", record)
    print("wrote published_hashes_signed.json (serial=1)")
    print("pin this publisher public key out-of-band (%s):" % publisher_id)
    print("  " + public_key_b64(publisher_private.public_key()))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
