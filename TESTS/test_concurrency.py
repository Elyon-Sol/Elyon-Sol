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
