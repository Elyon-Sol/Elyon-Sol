from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from IMPLEMENTATION.evaluator import evaluate


TEST_MANIFEST = {
    "version": "1.0",
    "interaction_type": "synthetic_ct_authorization",
    "AR": ["identity", "role", "doctor_authorized"],
    "R": ["session", "request", "patient_access"],
}

SHA = "a21dea8b79d459bd700ca44a30c2ca4a6efbee1447708cbc12c0bbb322d823b8"

results = []
results_lock = Lock()


AUTHORIZED_CTX = {
    "AP": ["identity", "role", "doctor_authorized"],
    "OP": ["session", "request", "patient_access"],
    "ccs_valid": True,
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256": SHA,
}

UNAUTHORIZED_CTX = {
    "AP": ["identity", "role"],
    "OP": ["session", "request", "patient_access"],
    "ccs_valid": True,
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256": SHA,
}


def run_authorized():
    result = evaluate(AUTHORIZED_CTX, TEST_MANIFEST)

    with results_lock:
        results.append(result)


def run_unauthorized():
    result = evaluate(UNAUTHORIZED_CTX, TEST_MANIFEST)

    with results_lock:
        results.append(result)


def test_concurrent_authority_isolation():
    results.clear()

    with ThreadPoolExecutor(max_workers=20) as executor:
        for _ in range(50):
            executor.submit(run_authorized)

        for _ in range(50):
            executor.submit(run_unauthorized)

    eligible = results.count("ELIGIBLE")
    refuse = results.count("REFUSE")

    assert eligible == 50
    assert refuse == 50
    assert len(results) == 100

from IMPLEMENTATION.replay.receipt import create_receipt, verify_receipt


def make_receipt(request_id, ctx):
    terminal_state = evaluate(ctx, TEST_MANIFEST)

    return create_receipt(
        request_id=request_id,
        terminal_state=terminal_state,
        manifest_version=TEST_MANIFEST["version"],
        manifest_sha256=SHA,
        refusal_reason_code=None if terminal_state == "ELIGIBLE" else "REF_CONCURRENT_AUTHORITY_GAP",
        timestamp="2026-05-12T00:00:00+00:00",
    )


def test_concurrent_replay_receipts_match_isolated_receipts():
    isolated_authorized = make_receipt("REQ-AUTH-001", AUTHORIZED_CTX)
    isolated_unauthorized = make_receipt("REQ-UNAUTH-001", UNAUTHORIZED_CTX)

    concurrent_receipts = {}

    def run_receipt(request_id, ctx):
        receipt = make_receipt(request_id, ctx)
        with results_lock:
            concurrent_receipts[request_id] = receipt

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_receipt, "REQ-AUTH-001", AUTHORIZED_CTX)
        executor.submit(run_receipt, "REQ-UNAUTH-001", UNAUTHORIZED_CTX)

    assert concurrent_receipts["REQ-AUTH-001"] == isolated_authorized
    assert concurrent_receipts["REQ-UNAUTH-001"] == isolated_unauthorized

    assert verify_receipt(concurrent_receipts["REQ-AUTH-001"]) is True
    assert verify_receipt(concurrent_receipts["REQ-UNAUTH-001"]) is True

    assert concurrent_receipts["REQ-AUTH-001"]["terminal_state"] == "ELIGIBLE"
    assert concurrent_receipts["REQ-UNAUTH-001"]["terminal_state"] == "REFUSE"
    assert concurrent_receipts["REQ-AUTH-001"]["receipt_sha256"] != concurrent_receipts["REQ-UNAUTH-001"]["receipt_sha256"]


BAD_SHA_CTX = {
    "AP": ["identity", "role", "doctor_authorized"],
    "OP": ["session", "request", "patient_access"],
    "ccs_valid": True,
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256": "BAD_MANIFEST_SHA",
}


def run_bad_sha():
    result = evaluate(BAD_SHA_CTX, TEST_MANIFEST)

    with results_lock:
        results.append(result)


def test_concurrent_manifest_sha_fault_fails_closed():
    results.clear()

    with ThreadPoolExecutor(max_workers=20) as executor:
        for _ in range(50):
            executor.submit(run_authorized)

        for _ in range(50):
            executor.submit(run_bad_sha)

    eligible = results.count("ELIGIBLE")
    refuse = results.count("REFUSE")

    assert eligible == 50
    assert refuse == 50
    assert len(results) == 100


import copy
import time


MUTABLE_MANIFEST = {
    "version": "1.0",
    "interaction_type": "synthetic_ct_authorization",
    "AR": ["identity", "role", "doctor_authorized"],
    "R": ["session", "request", "patient_access"],
}


def run_mutating_authorized():
    local_manifest = copy.deepcopy(MUTABLE_MANIFEST)

    result = evaluate(AUTHORIZED_CTX, local_manifest)

    with results_lock:
        results.append(result)


def mutate_manifest_during_execution():
    time.sleep(0.001)

    MUTABLE_MANIFEST["AR"] = ["identity"]


def test_manifest_mutation_during_concurrent_evaluation():
    results.clear()

    MUTABLE_MANIFEST["AR"] = [
        "identity",
        "role",
        "doctor_authorized",
    ]

    with ThreadPoolExecutor(max_workers=20) as executor:

        for _ in range(50):
            executor.submit(run_mutating_authorized)

        executor.submit(mutate_manifest_during_execution)

    eligible = results.count("ELIGIBLE")
    refuse = results.count("REFUSE")

    assert eligible == 50
    assert refuse == 0
    assert len(results) == 50
