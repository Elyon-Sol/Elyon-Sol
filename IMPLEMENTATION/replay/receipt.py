"""
Replay receipts.

Canonicalization (SES-5 / VL-143): canonical_json is REUSED from
envelope.py — ONE canonicalization repo-wide (sort_keys, no whitespace,
ensure_ascii=True). The previous LOCAL definition here used
ensure_ascii=False and diverged from the envelope / grant /
published-record canonicalization on non-ASCII input (the cross-component
footgun recorded OPEN at VL-141 and pinned at
TESTS/adversarial/test_seam_canonicalization.py). Receipts are ephemeral
(created and verified in-process; none are persisted), so unifying on the
envelope's ensure_ascii=True changes receipt bytes only for non-ASCII
field values and leaves the envelope path — and therefore decision_sha256
and the deployed chain — byte-identical.
"""
import hashlib
from datetime import datetime, timezone

from IMPLEMENTATION.envelope import canonical_json


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_receipt(
    *,
    request_id,
    terminal_state,
    manifest_version,
    manifest_sha256,
    refusal_reason_code=None,
    timestamp=None,
):
    receipt = {
        "request_id": request_id,
        "terminal_state": terminal_state,
        "manifest_version": manifest_version,
        "manifest_sha256": manifest_sha256,
        "refusal_reason_code": refusal_reason_code,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }

    receipt["receipt_sha256"] = sha256_text(canonical_json(receipt))

    return receipt


def verify_receipt(receipt):
    provided = receipt.get("receipt_sha256")
    if not isinstance(provided, str):
        return False

    body = dict(receipt)
    body.pop("receipt_sha256", None)

    expected = sha256_text(canonical_json(body))
    return provided == expected
