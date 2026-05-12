from IMPLEMENTATION.replay.receipt import create_receipt, verify_receipt


SHA = "a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8"


def test_receipt_hash_is_deterministic_with_fixed_timestamp():
    r1 = create_receipt(
        request_id="req-001",
        terminal_state="REFUSE",
        manifest_version="1.0",
        manifest_sha256=SHA,
        refusal_reason_code="REF_AC3_AUTHORITY_MISSING",
        timestamp="2026-05-12T00:00:00+00:00",
    )

    r2 = create_receipt(
        request_id="req-001",
        terminal_state="REFUSE",
        manifest_version="1.0",
        manifest_sha256=SHA,
        refusal_reason_code="REF_AC3_AUTHORITY_MISSING",
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert r1["receipt_sha256"] == r2["receipt_sha256"]
    assert verify_receipt(r1) is True


def test_receipt_detects_tampering():
    receipt = create_receipt(
        request_id="req-002",
        terminal_state="ELIGIBLE",
        manifest_version="1.0",
        manifest_sha256=SHA,
        timestamp="2026-05-12T00:00:00+00:00",
    )

    receipt["terminal_state"] = "REFUSE"

    assert verify_receipt(receipt) is False
