
### VL-037 - 2026-05-29 - T-G4-build: target-side envelope verifier; first G4 build increment (delivery deferred to VL-038)

**Status:** COMMITTED
**Author:** Claude (working session with the project author)
**Classification:** trajectory move per VL-017a's distinction (a new
`IMPLEMENTATION/` module + two new `TESTS/adversarial/` files; structural-doc
updates only in STATE.md, this ledger, `docs/restructure/04_current_vs_claimed.md`
G4 row, and `docs/restructure/06_spec_to_code_traceability.md` section-13 row
note). No canon/manifest/spec/pep.py change.

**Verifies:** `IMPLEMENTATION/verifier.py` lands per
`docs/restructure/08_enforcement_design.md` section 8 step 1: the
delivery-agnostic, target-side verifier, the first G4 (non-bypassable
enforcement) build increment. `verify_envelope(envelope, interaction,
target_url) -> {"accepted": bool, "reason": str}` performs, in order: (1) a
structural presence guard (a non-dict, or a dict missing a required key,
returns `REF_VERIFY_ENVELOPE_ABSENT`; this also guards `reassert()`'s key
accesses so a malformed envelope rejects cleanly rather than raising); (2)
`envelope.reassert()` for currency plus integrity (any outcome other than
REASSERTED rejects: INVALIDATED -> `REF_VERIFY_REASSERT_INVALIDATED`,
RE-EVALUATE-REQUIRED -> `REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED`); (3) a
binding check comparing the envelope's `request_context` (AP, OP, context,
expected_manifest_version, expected_manifest_sha256) and `target_url` against
the live interaction (mismatch -> `REF_VERIFY_BINDING_MISMATCH`); (4) accept
with reason `REASSERTED_AND_BOUND`. The verifier reuses `reassert()` as-is
(canon section 13 revalidation) and operationalizes the section 11.1
interaction identity at the target side; it introduces no new canonical
invariant (artifact 08 section 5) and is non-executing (canon section 14
holds). It wires nothing into `pep.py`; delivery is VL-038. G4 does NOT
transition to RESOLVED: the verifier has no caller, so bypassability is
unchanged.

**The Q5 split, realized in code.** Per artifact 08 section 4.2, `reassert()`
closes envelope authenticity (`decision_sha256` covers `request_context` and
`target_url`; a forged or mutated envelope fails Row 2 -> INVALIDATED, closing
forgery A2) but NOT interaction binding: `reassert()` compares only
repository-state hashes and never compares `request_context` to a live
interaction, so a genuine current envelope for interaction X REASSERTS against
a different forwarded body Y. The binding check is what closes same-state
replay A3 (artifact 08 section 7). The verifier composes both: `reassert()`
for authenticity plus currency, the binding check for interaction identity.

**Reject vocabulary.** A closed `REF_VERIFY_*` set (parallel to
`request_validator.py`'s `REF_SCHEMA_*` convention): one code per `reassert()`
non-REASSERTED outcome, one presence code, one binding code -
`REF_VERIFY_ENVELOPE_ABSENT`, `REF_VERIFY_REASSERT_INVALIDATED`,
`REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED`, `REF_VERIFY_BINDING_MISMATCH`. The
author locked the tighter set at Checkpoint A (one binding code rather than
splitting `target_url` out; one absent code rather than splitting malformed
out). Accept reason `REASSERTED_AND_BOUND` (not a refusal code). AP and OP are
compared as canon section 11.5/11.6 sets, normalized symmetrically on both
sides (`sorted(set(...))`, parity with `request_validator._normalize_set_field`);
`context` by `canonical_json` equality; `target_url` and the manifest-pinning
fields by string equality.

**G5 plus A1 named, not built (Decision F).** `reassert()` reads its comparison
hashes from local disk (`CANON/canon.lock`, `IMPLEMENTATION/evaluator.py`, the
live manifest), valid for this co-located build and tests. A cross-host target
needs an authentic, current, published hash source, which is gap G5 (artifact
08 section 6, Decision E1); it is named as the deployment precondition in the
module docstring and is NOT built. A1 (a caller that never routes) is named as
closeable only by a target-side policy refusing un-attested calls (artifact 08
section 4.4); the verifier is necessary-but-not-sufficient.

#### Tests (Decision D canon-derived; Decision E bypass)

`TESTS/adversarial/test_verifier.py` adds 11 tests, each docstring citing canon
section 13 / 11.1 / 11.5-11.6 / 12.4 and/or artifact 08 sections 4.2 / 4.4 / 7
/ 8: accept (valid, current, bound); the four `reassert()` rows (tamper Row 2
-> INVALIDATED; canon Row 1 -> INVALIDATED; evaluator Row 3 ->
RE-EVALUATE-REQUIRED; manifest Row 4 -> RE-EVALUATE-REQUIRED); absent envelope
(None); malformed envelope (no raise); replay binding-mismatch (the
load-bearing A3 case); target_url mismatch; AP/OP normalization parity (accept
under unsorted/duplicated live sets); context binding (equal accepts, differing
rejects). Per VL-037 constraint (i): no hash-value pinning; the expected
manifest sha is derived live via `manifest_sha256()`; envelopes are built with
a pinned `timestamp_utc`.

`TESTS/adversarial/test_bypass.py` adds 2 PASSING (not xfail) A1-bypass tests
per Decision E: a direct-to-target POST (bypassing `/governed-call`) reaches a
minimal target app carrying no envelope; and `verify_envelope(None, ...)`
rejects with `REF_VERIFY_ENVELOPE_ABSENT`, documenting that the only defense
against A1 is a target-side verify policy.

#### Checkpoint results

- **Checkpoint A (contract + reject set + test enumeration):** presented and
  author-reviewed. The author locked the tighter reject set (one binding code,
  one absent code) and accepted the 11 + 2 test list. The `context`-equality
  default (canonical_json) was flagged `[INFERENCE]` (artifact 08 gap
  candidate 1).
- **Checkpoint B (spec-gap discovery, mandatory):** no halt-class spec gap. The
  smoke-surfaced normalization issue (Process finding 1) is governed by
  Decision C's existing "compared under the SAME normalization" wording, not a
  spec gap; no spec-revision pre-step.
- **Checkpoint C (implementation review):** the verifier executes nothing and
  performs no I/O beyond `reassert()`'s reads (canon section 14); introduces no
  new invariant (consumes `reassert()` / section 13, operationalizes section
  11.1); uses the `IMPLEMENTATION.` import prefix and is import-tested (VL-027);
  no out-of-scope file touched (Decision A); no real bug in `evaluator.py` /
  `envelope.py` / `request_validator.py` was silently worked around (constraint
  (l)) - the one bug found was in the verifier draft itself and was fixed
  openly.
- **Checkpoint D (pre-commit review):** ASCII byte-sweep (Python byte check,
  not `grep -P`, per VL-036 Finding 5) clean on `verifier.py`, both test files,
  and this entry; structural-doc consistency confirmed (artifact 04 G4 bullet +
  artifact 06 section-13 note + STATE.md item 31 + bullet); this entry
  header-anchored after `### VL-036 -`; pytest 119 passed + 0 xfailed in the
  author's real environment.

#### Process findings

1. **Asymmetric AP/OP normalization in the first verifier draft (caught by the
   sandbox smoke; positive).** The first draft normalized only the live
   interaction's AP/OP (`sorted(set(...))`) and compared against the envelope's
   `request_context` AP/OP as stored. `build_envelope` records AP/OP in input
   order (it does not re-sort; the PEP's `validate_request` had already sorted
   them in production), so a fixture building an envelope from an unsorted OP
   produced a stored OP that the live-side-only normalization did not match, and
   two accept-path tests false-failed. Fixed to symmetric set normalization on
   both sides, which is canon section 11.5/11.6 set semantics and exactly what
   Decision C's "compared under the SAME normalization" requires. An
   implementation bug, not a spec gap; no Checkpoint B halt. Same shape as
   VL-025's smoke and VL-034 Finding 4: the encouraged pre-commit smoke
   (constraint (c)) paid for itself.
2. **Section-sign (U+00A7) leak in chat prose (Lesson 7 stage 2; user-caught).**
   During the Checkpoint A review turn, Claude's chat prose used U+00A7 as
   shorthand for "section N". User-caught. New surface event in the recurring
   family (Greek letters VL-029 / VL-031; em-dashes VL-032 / VL-033; section
   sign VL-034 Finding 1 / VL-036 Finding 4). Confined to chat prose; never
   reached a committed file (the Checkpoint D byte-sweep confirmed
   `verifier.py`, the test files, and this entry clean). Stage 2 (drafting-time
   sweep) did not fire preemptively for chat prose; the family continues to
   recur in the chat-prose register specifically.
3. **Repo absent from the working environment at session start; full
   source-first read gated on uploads.** The session opened with only the
   opener uploaded; the load-bearing files arrived in three batches after Claude
   enumerated the checklist gap. The checklist hard gate (Lesson 3) held: no
   substantive verifier claim was made until "checklist complete; 17 files read"
   was stated. STATE.md and the ledger were oriented from the resume dump and
   re-read from disk at apply-script-construction time per Lesson 2.

#### Files affected

- `IMPLEMENTATION/verifier.py` (new; `verify_envelope()` + the `REF_VERIFY_*`
  vocabulary)
- `TESTS/adversarial/test_verifier.py` (new; 11 canon-derived tests)
- `TESTS/adversarial/test_bypass.py` (new; 2 honest A1-bypass tests)
- `docs/restructure/04_current_vs_claimed.md` (G4 row: VL-037 build bullet; G4
  stays open)
- `docs/restructure/06_spec_to_code_traceability.md` (section-13 row:
  target-side-verifier note; no status change)
- `STATE.md` (Last-updated + VL-037 current-verified-state bullet +
  Next-open-action item 31)
- `EVIDENCE/verification_ledger.md` (this entry)

#### Files NOT affected

- `IMPLEMENTATION/pep.py`, `envelope.py`, `evaluator.py`, `request_validator.py`
  (Decision A; delivery is VL-038)
- `CANON/*`, `MANIFEST/*`, `SPEC/*` (no canon/manifest/spec change)
- `docs/restructure/05_admissibility_envelope_spec.md`, `08_enforcement_design.md`
  (read as sources; not modified)
- `docs/methodology/*`
- `README.md`

#### Citation discipline

Per VL-012's self-referencing-hash finding: this entry does not cite its own
commit hash. Parent commit `e138cbf` (VL-036). Prior entries cited:

- VL-036 at commit `e138cbf`
- VL-035 at commit `cdeeb25`
- VL-034 at commit `1e6fb01`
- VL-033 at commit `5e2fab0`
- VL-032 at commit `7f41615`
- VL-031 at commit `6369eac`

No cross-model verification of VL-037 was scheduled (Decision B; post-build
cross-model verification was optional and not elected, since Checkpoint B
surfaced no contestable design choice - the normalization fix was governed by
existing Decision C wording). The 13 tests are individually verifiable against
canon section 13 / 11.1 and artifact 08 via their docstrings; the suite is
verified green (119/119) in the author's real environment.

#### Gap candidates

1. **`context` equality semantics (artifact 08 gap candidate 1, carried).** The
   verifier compares `context` by `canonical_json` equality `[INFERENCE]`;
   artifact 08 does not pin equality semantics for the free-form canon section
   11.1 C. A future spec edit (artifact 08 or 05) may pin this. Non-blocking; no
   test depends on a contestable reading (the context-binding test uses
   value-distinct dicts).
2. **`06_spec_to_code_traceability.md` section-14 row unchanged.** Section 14
   stays PARTIAL ("non-bypassable only for routed calls (G4)"); the verifier
   does not change it because it has no caller. When VL-038 wires delivery, the
   section-14 row and the G4 row both move.
3. **Verifier placement.** `IMPLEMENTATION/verifier.py` (not a target-side
   subpackage) per the opener default; revisit if VL-038's delivery
   architecture motivates a target-side package.

#### Next trajectory action

**VL-038 G4-delivery:** decide the delivery architecture (push vs caller-carry
vs target-pull; artifact 08 sections 4.3 and 9 open question 1), wire it into
`pep.py`, migrate `TESTS/test_pep.py` to the delivered wire shape, and connect
`verify_envelope()` as the target-side check. Push deepens the pre-existing
section-14 tension (artifact 08 section 5); weigh against caller-carry.
**G5 (durable verification)** is the named cross-host precondition and may merge
with or precede VL-038. T-bookkeeping (G1/G8/G9/G11/G14) and T-prose-drift
remain open with no priority blocker.
