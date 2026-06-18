"""
Gate-side issuance log for Elyon-Sol (VL-099).

Built per docs/restructure/28_issuance_log_spec.md from primary sources
IMPLEMENTATION/pep.py and docs/restructure/26_envelope_inspector_spec.md
(read in full in the VL-099 session per SESSION_PROTOCOL step 4).

One JSONL line per signed ELIGIBLE envelope, written at issuance time by
pep.py's ELIGIBLE branch (after sign_envelope, before the upstream push,
inside the fail-closed catch), in exactly the shape
`python -m IMPLEMENTATION.envelope_inspector reconcile --issued`
consumes. This gives the VL-097 reconciler its gate-produced left-hand
side: without it, "every executed action maps to an issued envelope"
has no issuance record to check against.

Default-off: pep.py logs only when a log is injected
(pep._INJECTED_ISSUANCE_LOG) or ELYON_ISSUANCE_LOG_PATH is set; with
neither, the default path is byte-behavior-identical to pre-VL-099.

Fail-closed (canon section 9): pep.py treats an append failure as
REF_PEP_FAIL_CLOSED and never calls the target - a gate CONFIGURED to
log must not issue what it cannot record. The audit-trail guarantee
outranks availability (the same trade the shared replay cache makes,
VL-094).

Concurrency (spec 28 section 2.1, recorded honestly): O_APPEND
single-line writes are atomic for same-host writers at envelope sizes,
and the gate is single-process per instance. A horizontally-scaled
deployment gives each instance its own log file and concatenates for
audit; reconcile() takes a list, and decision_ids are unique per
issuance (VL-066), so concatenation order does not change verdicts.
"""

import os
from typing import Any, Dict, Optional

from IMPLEMENTATION.envelope import canonical_json


ISSUANCE_LOG_PATH_ENV = "ELYON_ISSUANCE_LOG_PATH"


class JsonlIssuanceLog:
    """Append-only JSONL issuance log. One canonical_json line per
    envelope (sorted keys, no whitespace, ASCII - envelope.py's one
    canonical form), flush + fsync per line: an audit log values
    durability over throughput (latency headroom per artifact 18)."""

    def __init__(self, path: str) -> None:
        self.path = path

    def append(self, envelope: Dict[str, Any]) -> None:
        line = canonical_json(envelope)
        with open(self.path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())


APPROVAL_LOG_PATH_ENV = "ELYON_APPROVAL_LOG_PATH"


class JsonlApprovalLog:
    """Append-only JSONL approval log (governance Feature 1, [FIX H8]).

    Records the approval lifecycle so `envelope_inspector reconcile_approvals`
    can prove no high-impact action was forwarded without a recorded human
    grant. Two record types, written by pep.governed_call:

      {"type": "approval_request", "decision_sha256", "approval_request_id"}
          - written at the 202 PENDING_APPROVAL hold.
      {"type": "grant_consumed", "decision_sha256", "approval_request_id",
       "grant_id", "approver_key_id"}
          - written in the approved leg, after the grant is claimed and BEFORE
            the forward (a consumed-but-not-forwarded record still proves the
            human grant existed; canon section 9 - record before you act).

    Same durability discipline as the issuance log (flush + fsync per line;
    canonical_json so the bytes are ASCII, sorted, whitespace-free)."""

    def __init__(self, path: str) -> None:
        self.path = path

    def append(self, record: Dict[str, Any]) -> None:
        line = canonical_json(record)
        with open(self.path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())


def approval_log_from_env() -> Optional["JsonlApprovalLog"]:
    """A JsonlApprovalLog when ELYON_APPROVAL_LOG_PATH is set, else None
    (parity with issuance_log_from_env; default None = no approval logging,
    byte-behavior-identical to pre-[FIX H8])."""
    path = os.environ.get(APPROVAL_LOG_PATH_ENV)
    if path:
        return JsonlApprovalLog(path)
    return None


def issuance_log_from_env() -> Optional[JsonlIssuanceLog]:
    """A JsonlIssuanceLog when ELYON_ISSUANCE_LOG_PATH is set, else None
    (parity with replay_cache_from_env, VL-076/094). Read per call so a
    harness can set/unset the variable without re-importing pep."""
    path = os.environ.get(ISSUANCE_LOG_PATH_ENV)
    if path:
        return JsonlIssuanceLog(path)
    return None
