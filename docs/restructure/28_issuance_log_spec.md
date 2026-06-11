# 28 - Gate-side issuance log spec (VL-099)

Status: CONFIRMED at VL-102 (drafted SINGLE-SOURCE in the VL-099 session from primary sources
`IMPLEMENTATION/pep.py` and `docs/restructure/26_envelope_inspector_spec.md`,
read in full this session per SESSION_PROTOCOL step 4 / VL-008
task-to-source binding). Cross-model verified at VL-102: every claim for this spec was classified Supported by two procedurally-clean verifier runs (Grok, OpenAI) under the committed VL-100 request (a third run, Gemini, was discarded as a VL-008 rule-(b) procedure violation; its one Contradicted was examined on the merits in VL-102 and found not to hold). Status: SINGLE-SOURCE -> CONFIRMED.

---

## 1. The gap this closes

The VL-097 reconciler consumes "a log of ISSUED envelopes", and the gate
does not persist one: every signed ELIGIBLE envelope leaves pep.py in the
push header and the response and is then gone from the gate's own record.
Without an issuance log, the reconciler's auditability property ("every
executed action maps to a signed, bound, single-use authorization, or is
named OUT_OF_SCOPE") has no gate-produced left-hand side; an auditor would
have to reconstruct issuance from target-side data, which is exactly the
log the audit is checking.

VL-099 gives the gate an issuance log: one JSONL line per signed ELIGIBLE
envelope, written at issuance time, in precisely the shape
`python -m IMPLEMENTATION.envelope_inspector reconcile --issued` consumes.

## 2. Placement and behavior

### 2.1 `IMPLEMENTATION/issuance_log.py` (the seam)

- `JsonlIssuanceLog(path)`: `append(envelope)` writes
  `canonical_json(envelope) + "\n"` (envelope.py's canonical form:
  sorted keys, no whitespace, ASCII) in append mode, flush + fsync per
  line (an audit log values durability over throughput; the gate's
  latency budget headroom is documented in artifact 18). One line ==
  one issuance == one JSON object: exactly the reconciler's input.
- `issuance_log_from_env()`: a `JsonlIssuanceLog` when
  `ELYON_ISSUANCE_LOG_PATH` is set, else `None` (parity with
  `replay_cache_from_env`, VL-076/094).
- Concurrency note (recorded honestly): O_APPEND single-line writes are
  atomic for same-host writers well past envelope sizes on Linux, and the
  gate is single-process per instance; a horizontally-scaled deployment
  gives each instance its own log file and concatenates for audit -
  `reconcile` takes a list, so concatenation order only affects which of
  two equally-matching envelopes is consumed first (and decision_ids are
  unique per issuance, VL-066, so in practice it does not).

### 2.2 pep.py wiring (this IS the wire; parity with VL-094)

- `_INJECTED_ISSUANCE_LOG` module slot (a harness/deploy shim) +
  `_get_issuance_log()` resolving injected-then-env, mirroring
  `_get_signing_key()`'s resolution order.
- In the ELIGIBLE branch, immediately AFTER `sign_envelope()` and INSIDE
  the same fail-closed try/except: if a log is configured, append the
  signed envelope. Placement rationale:
  - AFTER signing: the log records what was actually issued (signed,
    decision_id-bearing), not a pre-signature draft.
  - BEFORE the upstream push: issuance is the signing, not the delivery;
    an envelope that is issued but never delivered (push fails) must
    still be on the log (it exists; a capture of the response could
    still present it). The reconciler's UNUSED status is informational,
    so logged-but-never-executed is the correct audit picture.
  - FAIL-CLOSED on append failure (canon section 9): a gate CONFIGURED
    to log must not issue what it cannot record. An append exception
    becomes REF_PEP_FAIL_CLOSED and the target is never called - the
    audit-trail guarantee outranks availability, the same trade the
    shared replay cache makes (VL-094 honest ceiling).
- Default `None` (no injection, no env var): the default path is
  byte-behavior-identical to pre-VL-099. Build-then-wire discipline with
  the wire landing in the same increment but defaulting off.

## 3. What this enables

A deployment sets `ELYON_ISSUANCE_LOG_PATH` on the gate and records
executed actions target-side (the reference target's `received` list
plus its own identity and the envelope's decision_id); then

    python -m IMPLEMENTATION.envelope_inspector reconcile \
        --issued gate_issuance.jsonl --executed target_actions.jsonl \
        --keys pinned_keys.json

is a checkable claim over the deployment's history. The trustworthy-log
assumption (spec 26) now splits honestly in two: the gate's log is
produced by the gate itself at issuance (this spec); the target's action
log remains the target's to keep faithfully.

## 4. Honest scope (GR-3 / canon section 14)

No new canonical invariant; no evaluator / envelope / verifier /
manifest change; no `evaluator_sha256` roll. pep.py is intentionally
changed (the wire). Default-off, so every existing runner, test, proof,
and deployment is unchanged unless it opts in. Audit infrastructure;
NOT a G5 closer.

## 5. Tests

`TESTS/adversarial/test_issuance_log.py`: unit (one canonical line per
append, round-trips by json.loads, multi-append ordering); from_env
(None default / path set); pep wiring (ELIGIBLE appends exactly the
signed response envelope; REFUSE appends nothing; schema-refusal appends
nothing; no-log default unchanged; append failure -> 403
REF_PEP_FAIL_CLOSED with upstream NOT called); end-to-end (two admitted
calls logged, executed actions reconstructed from the captured pushes,
reconcile -> clean 2/2 matched with the gate's pinned key; a third
unlogged action -> OUT_OF_SCOPE).
