import hashlib
import json
from datetime import datetime, timezone


def canonical_json(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


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
