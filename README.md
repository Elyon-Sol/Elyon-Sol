# Elyon-Sol

A formal admissibility specification (v0.9.8.4) with a faithful
implementation of all three canonical invariants. The implemented
gate is a deterministic, fail-closed HTTP admission boundary
derived from the canonical whitepaper. It is opt-in,
pre-execution, and non-bypassable only by callers that route
through it.

Given an incoming request and a SHA256-pinned manifest, the gate
returns `ELIGIBLE` only if the caller's authority and operation
sets each satisfy the manifest's required sets, the manifest
version and hash match what the caller asserted, and the
canonical-continuity invariant holds. On `ELIGIBLE` the gate
constructs an admissibility envelope (a content-hashed record of
the decision context: canon, manifest, evaluator, request,
condition results, timestamp) and forwards the request to the
upstream target; the envelope is returned in the response. On
`REFUSE` or any exception the upstream is not called.

The canon defines three invariants. All three are FULL in the
post-VL-029 implementation:

- **Authority** (AC^3, canon sections 11.3 and 11.5) - FULL
- **Coverage** (T^26, canon sections 11.4 and 11.6) - FULL
- **Continuity** (CCS, canon sections 12-13) - FULL (envelope
  layer; see "Admissibility envelope" below)

The full spec-to-code traceability map with per-section status
is in `docs/restructure/06_spec_to_code_traceability.md` (15
FULL, 4 PARTIAL, 0 DRIFTED, 3 UNIMPLEMENTED, 3 N/A across 25
rows of canon sections). The remaining UNIMPLEMENTED rows are
canon sections marked optional / non-participating + one
structural-position question (D.3) recorded in the map.

Honest-provenance is a load-bearing project commitment: every
claim in this README is traceable to a canon clause, an
implementation construct, a test, and a ledger entry. The
restructure exists to make that traceability checkable. Named
build-outward items below.

---

## Orientation for new readers

This README is a starting point, not the source of truth. For
project continuity:

1. Read **`STATE.md`** first. It names the current verified
   state, the next open action, and the gaps. It is updated as
   the last step of each working session.
2. Read **`EVIDENCE/verification_ledger.md`** for the record of
   how each project claim became trusted. Every advance is a
   numbered `VL-NNN` entry. The current most-recent entry is
   VL-029 (commit `79012d7`).
3. Read **`docs/restructure/04_current_vs_claimed.md`** for the
   living gap document.
4. Read **`docs/restructure/06_spec_to_code_traceability.md`**
   for the per-canon-section implementation status.
5. Read **`CANON/canon.md`** (ASCII-safe transcription of
   `canon_v0.9.8.4.pdf`) as the derivation source for the spec
   and code.

Pass *artifacts*, never *verdicts*. A rating or approval is not
evidence; a derivation from primary sources (canon, code) is.

---

## Run

```bash
python -m uvicorn IMPLEMENTATION.pep:app --reload
```

Default address:

```
http://127.0.0.1:8000
```

---

## Endpoint

```
POST /governed-call
```

---

## Request shape

The wire shape is locked by `SPEC/request_schema.md` (G2 closed
in code at VL-019). The endpoint accepts a single JSON object:

```json
{
  "target_url": "https://upstream.example/path",
  "interaction": {
    "AP":                        ["identity", "role"],
    "OP":                        ["session", "request"],
    "context":                   {},
    "expected_manifest_version": "1.0",
    "expected_manifest_sha256":  "<64-char lowercase hex>"
  }
}
```

Field meanings, mapped to canon section 11 (the formal
interaction model):

| Field | Canon | Required | Notes |
|---|---|---|---|
| `target_url` | not canonical; PEP-wire concern | yes | RFC 3986 absolute URL the PEP forwards to on `ELIGIBLE` |
| `interaction.AP` | `AP(I)` section 11.5 | yes | Array of strings (set semantics) |
| `interaction.OP` | `OP(I)` section 11.6 | yes | Array of strings (set semantics) |
| `interaction.context` | `C` section 11.1 | yes | Free-form object; may be `{}` |
| `interaction.expected_manifest_version` | section 11.9 + envelope spec | yes | Caller-asserted; string-equal compared against the live manifest's `version` |
| `interaction.expected_manifest_sha256` | section 11.9 + section 12.4 + envelope spec | yes | Caller-asserted; 64-char lowercase hex; compared against the live manifest hash |

`AR(I)` and `R(I)` (required authorities and coverage) are
**not** caller-supplied; they are derived from
`MANIFEST/manifest.json` per canon section 11.9. The split is
load-bearing: a caller cannot weaken what is required by sending
different values.

Refer to `SPEC/request_schema.md` for the full schema including
provenance notes (G12, G13) and rejected shapes.

---

## Admissibility envelope

On `ELIGIBLE`, the response body carries an admissibility
envelope: a content-hashed record of the decision context.
Constructed at decision time per artifact 05 build-order step 5
(VL-029, commit `79012d7`); structure is locked by
`docs/restructure/05_admissibility_envelope_spec.md`. The
envelope is the runtime form of canonical CCS (canon section
12): a stored record of the system state at decision time that
allows continuity to be checked across transitions.

Ten top-level keys:

- `envelope_version` - schema version of the envelope itself
- `decision` - `"ELIGIBLE"` on the first issuance
- `target_url` - the upstream the gate forwarded to
- `canon` - `{version, canon_sha256}` pinning the canon at
  decision time
- `evaluated_against` - `{manifest_version, manifest_sha256}`
  pinning the manifest at decision time
- `request_context` - the normalized request (AP, OP, context,
  pinning fields)
- `evaluator` - `{version, evaluator_sha256}` pinning the
  evaluator source at decision time
- `condition_results` - `{ac3, t26, manifest_integrity, ccs}`;
  `ac3`/`t26`/`manifest_integrity` are booleans; `ccs` is
  `None` on first issuance (the section 12.3 continuity
  constraint is not applicable on first issuance) and a boolean
  on reassertion
- `timestamp_utc` - ISO 8601 UTC timestamp of envelope
  construction
- `decision_sha256` - SHA256 over the envelope minus
  `decision_sha256` and `timestamp_utc`, for reassertion
  verification

The envelope supports reassertion via `envelope.reassert()`:
given an envelope and the live system state, return one of
`{REASSERTED, INVALIDATED, RE-EVALUATE-REQUIRED}` with the
derived `ccs` value (True on REASSERTED, False on INVALIDATED
or RE-EVALUATE-REQUIRED, per canon section 12.4). Canon-derived
tests at `TESTS/adversarial/test_ccs_canonical.py` exercise the
section 11.9, 12.1, 12.3, 12.4, and 13 invariants directly,
with each test docstring citing the canon clause it verifies.

Envelopes are runtime return only (Decision D, VL-029);
persistence for durable external verification is build-outward
(see G5 below).

---

## Refusal vocabulary

Schema-layer refusals carry a `refusal_reason_code` in the 403
response. Seven codes named in the schema:

| Code | When emitted | Emitted by |
|---|---|---|
| `REF_SCHEMA_PARSE_ERROR` | Request body is not valid JSON | `IMPLEMENTATION/pep.py` |
| `REF_SCHEMA_TOP_LEVEL` | `target_url` or `interaction` missing or wrong outer type | `IMPLEMENTATION/request_validator.py` |
| `REF_SCHEMA_BAD_URL` | `target_url` not a syntactically valid absolute URL | validator |
| `REF_SCHEMA_FLAT_KEYS` | `AP` or `OP` at top level (the archived interception-proof shape; G2) | validator |
| `REF_SCHEMA_MANIFEST_PINNING_MISSING` | `expected_manifest_version` or `expected_manifest_sha256` absent from `interaction` | validator |
| `REF_SCHEMA_RESERVED_CCS` | A field key containing the substring `ccs` (case-insensitive) or matching `continuity_token` / `prior_state_hash` | validator |
| `REF_SCHEMA_TYPE_MISMATCH` | Field type does not match the schema (covers unknown-key inside `interaction` provisionally; see G14) | validator |

Evaluator-layer refusals (failed AC^3, failed T^26, manifest
integrity mismatch) return HTTP 403 with `terminal_state:
REFUSE` and no `refusal_reason_code`; the evaluator-layer
refusal vocabulary is not specified by the request schema.

PEP-layer fail-closed exceptions (upstream timeout, evaluator
exception, envelope construction exception) return 403 with
`refusal_reason_code: REF_PEP_FAIL_CLOSED`.

---

## Example - REFUSE (evaluator-layer)

Empty `AP` and `OP` pass the schema layer but fail AC^3 and
T^26 inside the evaluator:

```bash
curl -X POST http://localhost:8000/governed-call \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://httpbin.org/post",
    "interaction": {
      "AP": [],
      "OP": [],
      "context": {},
      "expected_manifest_version": "1.0",
      "expected_manifest_sha256": "REPLACE_WITH_LIVE_MANIFEST_SHA256"
    }
  }'
```

Response:

```json
{"detail":{"terminal_state":"REFUSE"}}
```

HTTP 403. Upstream is not called.

---

## Example - ELIGIBLE

A request whose `AP`/`OP` are supersets of the manifest's
`AR`/`R` and whose pinning fields match the live manifest:

```bash
curl -X POST http://localhost:8000/governed-call \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://httpbin.org/post",
    "interaction": {
      "AP": ["identity", "role"],
      "OP": ["session", "request"],
      "context": {},
      "expected_manifest_version": "1.0",
      "expected_manifest_sha256": "REPLACE_WITH_LIVE_MANIFEST_SHA256"
    }
  }'
```

Response (assuming the manifest hash matches the live file):

```json
{
  "decision": "ELIGIBLE",
  "envelope": {
    "envelope_version": "1.0",
    "decision": "ELIGIBLE",
    "target_url": "https://httpbin.org/post",
    "canon": {
      "version": "0.9.8.4",
      "canon_sha256": "<64-char hex>"
    },
    "evaluated_against": {
      "manifest_version": "1.0",
      "manifest_sha256": "<64-char hex>"
    },
    "request_context": {
      "AP": ["identity", "role"],
      "OP": ["session", "request"],
      "context": {},
      "expected_manifest_version": "1.0",
      "expected_manifest_sha256": "<64-char hex>"
    },
    "evaluator": {
      "version": "0.9.8.4",
      "evaluator_sha256": "<64-char hex>"
    },
    "condition_results": {
      "ac3": true,
      "t26": true,
      "manifest_integrity": true,
      "ccs": null
    },
    "timestamp_utc": "<ISO 8601 UTC>",
    "decision_sha256": "<64-char hex>"
  }
}
```

HTTP 200. Request forwarded to `target_url` once. The envelope
allows the caller (or an external verifier) to later check
continuity against the recorded state via
`envelope.reassert()`.

The `expected_manifest_sha256` value must equal the SHA256 of
the actual `MANIFEST/manifest.json` on disk. Compute it with:

```bash
sha256sum MANIFEST/manifest.json
```

---

## Tests

```bash
python -m pytest TESTS/
```

The authoritative test inventory and expected count for the
current HEAD are in `STATE.md` under "Current verified state"
and in the most recent `VL-NNN` ledger entry. This README does
not hardcode test counts; consult `STATE.md` for the count
pinned to the current commit.

Test files at the time of writing (subject to ledger updates):

- `TESTS/adversarial/test_request_schema.py` - schema refusal
  vocabulary, one test per refusal class plus parse-error and
  the positive accepting-shape case
- `TESTS/adversarial/test_envelope.py` - admissibility envelope
  structure and reassert() behavior; spec-derived tests citing
  `docs/restructure/05_admissibility_envelope_spec.md`
- `TESTS/adversarial/test_ccs_canonical.py` - canon-derived
  tests citing canon sections 11.9, 12.1, 12.3, 12.4, 13
  directly; the canonical-CCS verification surface
- `TESTS/test_adversarial_evaluator.py` - evaluator-layer
  regression: AC^3, T^26, manifest integrity
- `TESTS/test_pep.py` - PEP-layer behavior: evaluator REFUSE,
  ELIGIBLE forwarding, fail-closed on upstream error, manifest
  version drift, envelope emission on ELIGIBLE
- `TESTS/test_concurrency.py` - concurrency behavior
- `TESTS/test_replay_receipts.py` - replay-receipt subsystem

---

## Guarantees

- **Fail-closed enforcement.** Any exception in the PEP,
  evaluator, or envelope construction yields `REFUSE`; the
  upstream is not called.
- **No retries.** A REFUSE is terminal; the gate does not retry
  evaluation.
- **No fallback execution.** The gate has no path to ELIGIBLE
  that bypasses schema validation followed by evaluation
  followed by envelope construction.
- **Deterministic gating.** Given the same canon, manifest,
  evaluator, and request, the same decision is reached and the
  same envelope (modulo timestamp) is produced. The envelope's
  `decision_sha256` is reproducible.
- **Manifest pinning.** The caller asserts the manifest version
  and hash they reasoned against; a mismatch is refused at the
  evaluator layer.
- **Canonical continuity.** On reassertion (a re-check of a
  previously-issued envelope against the live system state),
  any change in canon, manifest, or evaluator hash invalidates
  the prior `ELIGIBLE` per canon section 12.4. Continuity does
  not persist across transitions without revalidation (canon
  section 13).

---

## Resolved gaps

The gap document at
`docs/restructure/04_current_vs_claimed.md` is the canonical
record. Resolved gaps as of HEAD:

- **G0** - CCS specification/implementation drift. **RESOLVED**
  at VL-029 (commit `79012d7`). Both halves closed:
  - **Rename half** (VL-012): the implemented function formerly
    mis-named `ccs_valid()` was renamed to
    `manifest_integrity_valid()` to reflect what it actually
    checks (manifest version + manifest SHA256). The name
    "CCS" was reserved in code and test IDs.
  - **Build half** (VL-029): canonical CCS (canon section 12
    transition invariant) implemented at the envelope layer
    via `envelope.build_envelope()` + `envelope.reassert()`.
    Wired into the gate by `pep.py` per artifact 05
    build-order step 5. Verified by nine canon-derived tests
    at `TESTS/adversarial/test_ccs_canonical.py`.
- **G2** - Request schema drift. **RESOLVED** at VL-019.
  Schema drafted (VL-014), cross-model verified (VL-015),
  interpretive corrections (VL-016), failing tests (VL-017),
  validator (VL-018), PEP wiring (VL-019).
- **G6, G10** - Resolved at VL-012 (manifest provenance
  fields).

See `docs/restructure/04_current_vs_claimed.md` "Resolved gaps"
section for the full record.

---

## Known limitations

The implementation is honest about what is and is not realized.
See `docs/restructure/04_current_vs_claimed.md` for the full
gap document with statuses, deltas, and required actions.

**Open and material:**

- **G3** - Public framing reframe. Pre-VL-029 public materials
  overclaimed implementation completeness relative to canon
  coverage. This README rewrite (initial pass at commit
  `5f833fb`) and the corresponding Zenodo addendum Revision 2
  (DOI `10.5281/zenodo.20387278`) closed the T-G3 trajectory
  at VL-030.
- **G4** - **The gate is opt-in, not enforced.** A caller can
  hit the target directly and bypass the PEP. The canon
  ("operates pre-execution," "non-executing governance
  substrate") does not explicitly claim non-bypassability, but
  a reader reasonably infers enforcement. Non-bypassable
  enforcement is scheduled in build-outward scope.
- **G5** - External verification is not durable. Interception
  proofs to date relied on a local process or an ephemeral
  webhook. The post-VL-029 envelope supports content-hashed
  reassertion, but envelopes are runtime return only;
  persistence (a target-side logging receiver committed to
  `EVIDENCE/proofs/`) is build-outward.
- **G7** - Tests are code-derived, not canon-derived.
  **PARTIALLY ADDRESSED** (VL-028 + VL-029): envelope domain
  closed via `TESTS/adversarial/test_ccs_canonical.py` (9
  canon-derived tests citing canon sections 11.9, 12.1, 12.3,
  12.4, 13). Evaluator-domain canon-derived tests (AC^3,
  T^26, manifest-integrity) remain code-derived and open as a
  future trajectory action.

**Bookkeeping (no operational impact, scheduled in a batch):**
G1, G8, G9, G11, G12 (canon-layer half), G13 (canon-layer half),
G14.

**Structural-position question:**

- **Appendix D.3** - The canon's worked example of an
  in-evaluate CCS-isolated failure (AC^3=1, T^26=1, CCS=0 ->
  REFUSE inside `evaluate()`) does not occur on first issuance
  in the post-VL-029 architecture because canonical CCS lives
  at the envelope layer (downstream of `evaluate()`); the
  CCS-isolated failure does occur at reassertion via the
  section-12.4 path. Recorded as UNIMPLEMENTED in artifact 06
  for honest accountability; close-out would be either a
  refactor pulling CCS into the in-evaluate pipeline or an
  envelope-on-refuse extension at pep.py.

---

## Repository structure

```
Elyon-Sol/
+-- .gitattributes               text-mode + ASCII-safe regime (VL-006/VL-009)
+-- .gitignore
+-- LICENSE
+-- README.md                    this file
+-- STATE.md                     project state; read this first
|
+-- CANON/                       LOCKED. Fixed point.
|   +-- canon_v0.9.8.4.pdf       immutable source of record
|   +-- canon.md                 ASCII-safe transcription (VL-006)
|   \-- canon.lock               sha256 of canon.md
|
+-- SPEC/                        derivation-faithful specifications
|   \-- request_schema.md        wire shape lock (VL-014..VL-019)
|
+-- IMPLEMENTATION/
|   +-- envelope.py              admissibility envelope: build_envelope, reassert (VL-025..VL-029)
|   +-- evaluator.py             AC^3, T^26, manifest_integrity_valid
|   +-- pep.py                   HTTP boundary; envelope emission on ELIGIBLE (VL-019, VL-029)
|   +-- request_validator.py     schema validator (VL-018)
|   +-- target.py                downstream target stub (for tests)
|   \-- replay/
|       \-- receipt.py           replay-receipt subsystem
|
+-- MANIFEST/
|   \-- manifest.json            SHA256-pinned (VL-010)
|
+-- TESTS/
|   +-- ADVERSARIAL_RESULTS.md
|   +-- test_adversarial_evaluator.py
|   +-- test_cases.json
|   +-- test_concurrency.py
|   +-- test_pep.py
|   +-- test_replay_receipts.py
|   \-- adversarial/
|       +-- test_ccs_canonical.py     canon-derived tests (VL-028)
|       +-- test_envelope.py          envelope spec-derived tests (VL-028)
|       \-- test_request_schema.py
|
+-- EVIDENCE/
|   +-- verification_ledger.md   append-only ledger (VL-NNN entries)
|   +-- proofs/                  current proof artifacts
|   \-- archive/                 retired evidence (NON-CURRENT headers)
|
+-- POE/                         proof-of-existence layer
|   +-- POE_MANIFEST.md
|   +-- POE_SHA256_HASHES.txt
|   \-- generate_poe_hashes.py
|
+-- docs/
|   +-- SESSION_PROTOCOL.md      session resume/close protocols
|   +-- MAINTENANCE_PROTOCOL.md  governance rules (GR-N entries)
|   +-- restructure/             Rev. 2 planning package
|   |   +-- 00_README.md
|   |   +-- 01_repository_structure.md   reconciled tree
|   |   +-- 02_honest_core_description.md
|   |   +-- 03_vocabulary_ledger.md
|   |   +-- 04_current_vs_claimed.md     gap document
|   |   +-- 05_admissibility_envelope_spec.md
|   |   +-- 06_spec_to_code_traceability.md
|   |   \-- canon_transcription_verification_report.md
|   \-- methodology/             reusable session patterns
|       +-- apply_script_template.py
|       +-- build_resumption_request_template.md
|       +-- verification_request_template.md
|       \-- session_mechanics_lessons.md
|
\-- scripts/
    +-- establish_ledger.sh
    +-- lock_canon.sh
    +-- append_vl008.sh
    +-- append_vl009.sh
    \-- append_vl010.sh
```

This listing is reconciled against
`docs/restructure/01_repository_structure.md` (the structural
diff-of-record at HEAD = 2db1807) and STATE.md citations of
files added after artifact 01 was last touched (VL-011's
EVIDENCE reorganization, VL-014's `SPEC/request_schema.md`,
VL-017a/b's `docs/methodology/` templates, VL-018 follow-up's
`session_mechanics_lessons.md`, VL-025's `IMPLEMENTATION/envelope.py`,
VL-028's two `TESTS/adversarial/` test files). If this listing
diverges from the actual tree, `01_repository_structure.md` is
the source of truth and this README is the stale one.

---

## License

See `LICENSE` in the repository root.

---

## Status

- **Canon:** v0.9.8.4 (locked; corrections only by version
  increment per GR-1, ledger VL-007).
- **Implementation:** all three canonical invariants (AC^3,
  T^26, CCS) are FULL post-VL-029. G0 closed (rename half
  VL-012 + build half VL-029, commit `79012d7`).
- **Active trajectories** (post-VL-029, none blocking any
  other):
  - **T-G3**: public framing reframe (this README + Zenodo +
    external surfaces). VL-030 partial.
  - **T-07**: `docs/restructure/07_continuity_recursion.md`
    artifact drafting (newly schedulable per VL-023 + VL-024
    + VL-025-follow-up convergent confirmation).
  - **T-methodology**: bookkeeping commit absorbing accumulated
    methodology-promotion candidates from VL-025 through
    VL-029 (synthetic-fixture pattern, ASCII pre-check
    discipline, caller-enumeration symmetry per VL-029
    Finding 8).
  - **T-G7-eval**: canon-derived tests for the evaluator
    domain (AC^3, T^26, manifest-integrity) extending the
    VL-028 pattern.
  - **T-bookkeeping**: G1, G8, G9, G11, G14 batch.
- **Last ledger entry:** VL-029 at commit `79012d7`. See
  `git log EVIDENCE/verification_ledger.md` for the
  authoritative history.
