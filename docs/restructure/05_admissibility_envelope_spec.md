# Elyon-Sol  -  Admissibility Envelope Specification (Rev. 2)

**Status:** Draft for review. Derivation from locked canon, whitepaper v0.9.8.4 section 12-section 13.
**Reframe (Rev. 2):** The envelope is **not a new feature**. It is the **implementation of
canonical CCS**  -  the temporal continuity invariant the whitepaper already specifies in section 12
but which `ccs_valid()` does not currently implement (see Deliverable 04, gap G0).

---

## What changed from Rev. 1, and why

Rev. 1 presented the envelope as a continuity *enhancement*. Having now read the canon, that
was an undersell. Whitepaper section 12 defines CCS as `CCS(S_t, S_{t+1}, I)`  -  a relation over state
*transitions*. The implemented `ccs_valid()` is point-in-time only. The envelope's
reassertion protocol is precisely the missing transition logic. So:

- The envelope **introduces no new invariant.** This is consistent with the canon's repeated
  "no new invariants" constraint (section Abstract, section 8.4, Appendix D). The envelope *implements an
  existing one*  -  CCS as already specified.
- Every envelope field below is justified by a specific whitepaper clause. This artifact is
  the first in the repo built with explicit spec-to-code traceability (see Deliverable 06).

---

## Canon mapping  -  section 12/section 13 -> envelope mechanism

| Whitepaper clause | What it requires | Envelope mechanism |
|---|---|---|
| section 11.1 `I = (A, S, C, t)` | interaction has state + time | envelope records request context + timestamp + state hashes |
| section 12.1 transition `S_t -> S_{t+1}` | "any change in context, authority, coverage, or system state" | envelope pins the hashes that define a state; a hash change *is* a transition |
| section 12.3 continuity constraint | authority/coverage transitions justified; `d_{t+1} = u_{t+1} AND c_{t+1}` | `condition_results` block records `u`, `c`, `d`; reassertion re-checks consistency |
| section 12.4 / section 7 invalid transitions | manifest version change, role/authority schema change, identity mapping inconsistency | reassertion detects via `manifest_sha256` / `canon_sha256` / `evaluator_sha256` mismatch |
| section 13 "eligibility does not persist across transitions without revalidation" | a past ELIGIBLE is not durable | `reassert()` returns `RE-EVALUATE-REQUIRED` when state moved; eligibility is never assumed |
| section 9 reproducibility | identical inputs + same manifest -> identical results | canonical JSON serialization -> deterministic `decision_sha256` |

---

## Envelope structure

```json
{
  "envelope_version": "1.0",
  "decision": "ELIGIBLE",
  "canon": {
    "version": "0.9.8.4",
    "canon_sha256": "<hash of CANON/canon.md at decision time>"
  },
  "evaluated_against": {
    "manifest_version": "1.0",
    "manifest_sha256": "<hash of MANIFEST/manifest.json at decision time>"
  },
  "request_context": {
    "AP": ["identity", "role"],
    "OP": ["session", "request"],
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256": "<...>"
  },
  "evaluator": {
    "version": "0.9.8.4",
    "evaluator_sha256": "<hash of IMPLEMENTATION/evaluator.py>"
  },
  "condition_results": {
    "ac3": true,            // u  -  section 12.2 decision variable
    "t26": true,            // c  -  section 12.2 decision variable
    "manifest_integrity": true,   // point-in-time check (manifest_integrity_valid in code; renamed from ccs_valid in VL-012)
    "ccs": true             // d-consistency across transition  -  section 12.3; only meaningful on reassertion
  },
  "decision_sha256": "<hash over canonicalized envelope minus this field>",
  "timestamp_utc": "2026-05-14T00:00:00Z"
}
```

### Field rationale

- **`canon` block**  -  pins the decision to the locked canon (whitepaper version + hash). If
  `CANON/canon.lock` ever shows a different hash, every prior envelope provably predates a
  canon change. This makes "canon is locked" *enforceable*, not merely stated.
- **`evaluated_against`**  -  the manifest state, per section 11.9 ("the manifest must be
  deterministic, versioned, and integrity-verifiable").
- **`evaluator` block**  -  pins to the implementation. A changed evaluator hash means the
  decision logic itself moved (section 12.4-class transition).
- **`condition_results`**  -  note the explicit split. `manifest_integrity` is the point-in-time
  check, implemented in `IMPLEMENTATION/evaluator.py` as `manifest_integrity_valid()` (renamed
  from `ccs_valid` in VL-012; closes the rename half of G0 and resolves G6). `ccs` is the
  **true section 12 invariant**  -  decision consistency across a transition  -  and is only
  meaningfully evaluable at *reassertion* time, because it is inherently about `S_t -> S_{t+1}`.
  Implementing it is the G0 build track (open).
- **`decision_sha256`**  -  tamper-evidence. Canonical JSON (sorted keys, no whitespace),
  reusing the serialization discipline from the existing replay-receipt work.
- **`timestamp_utc`**  -  audit only; **excluded** from `decision_sha256` so the same decision
  is bit-identical regardless of issue time (preserves section 9 reproducibility).

---

## Reassertion protocol  -  this IS canonical CCS

`reassert(envelope)` implements section 13: eligibility does not persist across transitions without
revalidation.

```
reassert(envelope) -> REASSERTED | INVALIDATED | RE-EVALUATE-REQUIRED
```

| Condition | Result | Canon basis |
|---|---|---|
| `canon_sha256` != live canon hash | `INVALIDATED` | canon changed; envelope predates current rules |
| `decision_sha256` does not verify | `INVALIDATED` | tampered/corrupt envelope |
| `evaluator_sha256` != live evaluator hash | `RE-EVALUATE-REQUIRED` | section 12.4  -  decision logic transition |
| `manifest_sha256` != live manifest hash | `RE-EVALUATE-REQUIRED` | section 7/section 12.4  -  manifest version/schema transition |
| all hashes match AND `decision_sha256` verifies | `REASSERTED` | section 12.3  -  continuity holds; `d_{t+1} = d_t` provably |

`REASSERTED` is the only state in which a past `ELIGIBLE` may be honored without
re-evaluation. This is exactly section 13's requirement, made operational.

---

## Relationship to the locked canon  -  explicit

- The envelope **modifies no canon text** and **introduces no new invariant**. It implements
  CCS *as already written in section 12*. This is the distinction that matters: prior to the
  envelope, the repo *claimed* CCS and *implemented* a point-in-time substitute (G0). The
  envelope closes that gap by building the thing the canon already specified.
- If canon is ever revised, that is a canon-version event: every envelope under the old
  `canon_sha256` is `INVALIDATED` automatically. Lock and envelope are mutually reinforcing  -
  the lock makes the envelope meaningful; the envelope makes the lock observable.

---

## Open questions for review

1. **`ccs` field on first issuance.** On the initial decision there is no `S_t`  -  only
   `S_{t+1}`. Proposal: on first issuance `ccs` is recorded as `null` or `"INITIAL"`, and
   becomes a true boolean only at first reassertion. Confirm.
2. **Where envelopes live.** Runtime return value from `pep.py`, persisted log under
   `EVIDENCE/`, or both. Recommend both.
3. **Envelope on the forwarded call (bypassability thread  -  G4).** If `pep.py` attaches the
   envelope to the forwarded request and the target verifies `decision_sha256` against
   Elyon-Sol's published canon hash, the target can refuse calls lacking a valid envelope.
   That is a concrete first step toward non-bypassable enforcement. Flagged as build-outward,
   not part of the CCS implementation itself.

---

## Build order

1. `SPEC/request_schema.md`  -  lock the request shape (the envelope embeds it).
2. Rename `ccs_valid()` -> `manifest_integrity_valid()`; reserve "CCS" (gaps G0/G6). **Done in VL-012 (commit 8ba88cf).**
3. `IMPLEMENTATION/envelope.py`  -  `build_envelope(...)` and `reassert(...)`.
4. `TESTS/adversarial/test_envelope.py`  -  construction determinism, the reassertion table,
   tamper detection. **Plus** a canon-derived `test_ccs_canonical.py` that cites section 12  -  it
   should fail until step 3 lands, then pass. That failing test is the honest G0 signal.
5. Wire `pep.py` to emit an envelope per decision.
6. Only then: explore open question 3 (envelope-on-forwarded-call).
