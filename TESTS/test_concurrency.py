from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock

from IMPLEMENTATION.evaluator import evaluate, load_manifest, manifest_sha256


# VL-053: fixtures repointed to the on-disk manifest. Before VL-053,
# TEST_MANIFEST / MUTABLE_MANIFEST carried a doctor_authorized /
# patient_access schema that DIVERGED from MANIFEST/manifest.json; the
# tests passed only because manifest_integrity_valid() read the sha from
# disk (G11, the manifest-source asymmetry surfaced at VL-012) while AC^3
# / T^26 evaluated the divergent argument -- a split-source ELIGIBLE. The
# VL-053 divergence guard fails closed on a manifest that is not the
# on-disk source, so the fixtures are repointed to load_manifest() and the
# authorized/unauthorized contrast is rebuilt on the on-disk AR/R sets.
# SHA is derived live (no literal hash pin; survives a GR-1 event).
TEST_MANIFEST = load_manifest()

SHA = manifest_sha256()

results = []
results_lock = Lock()


# Authorized: AP/OP each satisfy the on-disk AR=[identity, role] /
# R=[session, request] and pin the live version + sha -> ELIGIBLE.
AUTHORIZED_CTX = {
    "AP": ["identity", "role"],
    "OP": ["session", "request"],
    "expected_manifest_version": TEST_MANIFEST["version"],
    "expected_manifest_sha256": SHA,
}

# Unauthorized: AP omits the required "role" -> AC^3 fails -> REFUSE.
UNAUTHORIZED_CTX = {
    "AP": ["identity"],
    "OP": ["session", "request"],
    "expected_manifest_version": TEST_MANIFEST["version"],
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
    "AP": ["identity", "role"],
    "OP": ["session", "request"],
    "expected_manifest_version": TEST_MANIFEST["version"],
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


# VL-053: repointed to the on-disk manifest (see the fixture note above).
MUTABLE_MANIFEST = load_manifest()

# VL-073 follow-up 2: deterministic snapshot/mutation ordering (was a
# time.sleep(0.001) race that the first real CI run flaked at 48/50).
_snapshot_lock = Lock()
_snapshot_count = [0]
_all_snapshotted = Event()


def run_mutating_authorized():
    local_manifest = copy.deepcopy(MUTABLE_MANIFEST)

    # Signal that this task has taken its pre-mutation snapshot, so the mutation
    # fires only AFTER all 50 snapshots (VL-073 follow-up 2). The prior version
    # relied on mutate_manifest_during_execution sleeping 0.001s; under the CI
    # runner's thread scheduling 2 of 50 tasks snapshotted AFTER the mutation and
    # were (correctly) guard-refused -> 48 ELIGIBLE, failing the over-strict
    # eligible==50 assertion. Ordering the mutation after all snapshots makes the
    # intended property (pre-mutation snapshots all evaluate ELIGIBLE) hold
    # deterministically; the guard's REFUSE-on-post-mutation-snapshot path is
    # covered for real by test_manifest_integrity_rejects_divergent_manifest.
    with _snapshot_lock:
        _snapshot_count[0] += 1
        if _snapshot_count[0] >= 50:
            _all_snapshotted.set()

    result = evaluate(AUTHORIZED_CTX, local_manifest)

    with results_lock:
        results.append(result)


def mutate_manifest_during_execution():
    # Deterministic replacement for time.sleep(0.001): wait until all 50
    # authorized tasks have snapshotted, then mutate. No deadlock - the mutation
    # occupies at most one of the 20 pool workers and the authorized tasks never
    # block; the timeout is a safety net only.
    _all_snapshotted.wait(timeout=30)

    MUTABLE_MANIFEST["AR"] = ["identity"]


def test_manifest_mutation_during_concurrent_evaluation():
    results.clear()
    _snapshot_count[0] = 0
    _all_snapshotted.clear()

    # VL-053: a deep-copied snapshot taken BEFORE the concurrent mutation
    # is on-disk-consistent and evaluates ELIGIBLE; the VL-053 divergence
    # guard would fail-close a snapshot taken AFTER the mutation (AR
    # diverges from the on-disk source). The 50 authorized tasks submit
    # before the mutation task (which sleeps 0.001s), so all 50 snapshot
    # the pre-mutation manifest -> 50 ELIGIBLE. The guard makes this timing
    # assumption load-bearing (pre-VL-053 a post-mutation AR shrink still
    # evaluated ELIGIBLE); recorded as a VL-053 finding.
    MUTABLE_MANIFEST["AR"] = ["identity", "role"]

    with ThreadPoolExecutor(max_workers=20) as executor:

        for _ in range(50):
            executor.submit(run_mutating_authorized)

        executor.submit(mutate_manifest_during_execution)

    eligible = results.count("ELIGIBLE")
    refuse = results.count("REFUSE")

    assert eligible == 50
    assert refuse == 0
    assert len(results) == 50
