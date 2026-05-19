# Elyon-Sol

A formal admissibility specification (v0.9.8.4) with a faithful
partial implementation. The implemented gate is a deterministic,
fail-closed HTTP admission boundary derived from the canonical
whitepaper. It is opt-in, pre-execution, and non-bypassable only
by callers that route through it.

Given an incoming request and a SHA256-pinned manifest, the gate
returns `ELIGIBLE` only if the caller's authority set and
operation set each satisfy the manifest's required sets and the
manifest version and hash match what the caller asserted;
otherwise `REFUSE`. On `ELIGIBLE` the request is forwarded to
the upstream target; on `REFUSE` or any exception the upstream
is not called.

The canon defines three invariants:

- **Authority** (AC^3, canon sections 11.3 and 11.5) - FULL
- **Coverage** (T^26, canon sections 11.4 and 11.6) - FULL
- **Continuity** (CCS, canon sections 12-13) - DRIFTED; see
  "Known limitations" below

The implementation faithfully realizes AC^3, T^26, and the
manifest-integrity layer. Canonical CCS is not implemented. The
gap is anchored as G0 in
`docs/restructure/04_current_vs_claimed.md`.

---

## Orientation for new readers

This README is a starting point, not the source of truth. For
project continuity:

1. Read **`STATE.md`** first. It names the current verified
   state, the next open action, and the gaps. It is updated as
   the last step of each working session.
2. Read **`EVIDENCE/verification_ledger.md`** for the record of
   how each project claim became trusted. Every advance is a
   numbered `VL-NNN` entry.
3. Read **`docs/restructure/04_current_vs_claimed.md`** for the
   living gap document.
4. Read **`CANON/canon.md`** (ASCII-safe transcription of
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
exception) return 403 with `refusal_reason_code:
REF_PEP_FAIL_CLOSED`.

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
  "terminal_state": "ELIGIBLE",
  "upstream_status": 200,
  "upstream_response": "..."
}
```

HTTP 200. Request forwarded to `target_url` once.

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
and in the most recent `VL-NNN` ledger entry. Per G1, this
README does not hardcode test counts; consult `STATE.md` for
the count pinned to the current commit.

Test files at the time of writing (subject to ledger updates):

- `TESTS/adversarial/test_request_schema.py` - schema refusal
  vocabulary, one test per refusal class plus parse-error and
  the positive accepting-shape case
- `TESTS/test_adversarial_evaluator.py` - evaluator-layer
  regression: AC^3, T^26, manifest integrity
- `TESTS/test_pep.py` - PEP-layer behavior: evaluator REFUSE,
  ELIGIBLE forwarding, fail-closed on upstream error, manifest
  version drift
- `TESTS/test_concurrency.py` - concurrency behavior
- `TESTS/test_replay_receipts.py` - replay-receipt subsystem

---

## Guarantees

- **Fail-closed enforcement.** Any exception in the PEP or
  evaluator yields `REFUSE`; the upstream is not called.
- **No retries.** A REFUSE is terminal; the gate does not retry
  evaluation.
- **No fallback execution.** The gate has no path to ELIGIBLE
  that bypasses schema validation followed by evaluation.
- **Deterministic gating.** Given the same request and manifest,
  the same decision is reached.
- **Manifest pinning.** The caller asserts the manifest version
  and hash they reasoned against; a mismatch is refused at the
  evaluator layer.

---

## Known limitations

The implementation is honest about what is and is not realized.
See `docs/restructure/04_current_vs_claimed.md` for the full
gap document with statuses, deltas, and required actions.

**Open and material:**

- **G0** - Canonical CCS not implemented. The implemented
  `manifest_integrity_valid()` is a point-in-time check; the
  canonical CCS invariant (canon section 12) is a temporal
  invariant over state transitions. The two are not the same
  invariant. The rename half is closed (VL-012); the build
  half is the next active track after the G2 schema work,
  gated on the admissibility envelope (Deliverable 05).
- **G3** - Public framing has overclaimed implementation
  completeness relative to canon coverage; this README and the
  spec-to-code traceability map are the corrective surface.
- **G4** - **The gate is opt-in, not enforced.** A caller can
  hit the target directly and bypass the PEP. The canon
  ("operates pre-execution," "non-executing governance
  substrate") does not explicitly claim non-bypassability, but
  a reader reasonably infers enforcement. Non-bypassable
  enforcement is scheduled in build-outward scope.
- **G5** - External verification is not durable. Interception
  proofs to date relied on a local process or an ephemeral
  webhook. Until a target-side logging receiver is committed to
  `EVIDENCE/proofs/`, the property is "observable at the PEP,"
  not "externally verified."
- **G7** - Tests are code-derived, not canon-derived. The
  current suite confirms implemented behavior; it cannot detect
  drift from canon. Canon-derived tests are a separate
  category and are not yet present.

**Bookkeeping (no operational impact, scheduled in a batch):**
G1, G8, G9, G11, G12 (canon-layer half), G13 (canon-layer half),
G14.

**Resolved gaps** are documented in
`docs/restructure/04_current_vs_claimed.md` under
"Resolved gaps."

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
|   +-- evaluator.py             AC^3, T^26, manifest_integrity_valid
|   +-- pep.py                   HTTP boundary; validator wiring (VL-019)
|   +-- request_validator.py     schema validator (VL-018)
|   +-- server.py                HTTP server entry
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
`session_mechanics_lessons.md`). If this listing diverges from
the actual tree, `01_repository_structure.md` is the source of
truth and this README is the stale one.

---

## License

See `LICENSE` in the repository root.

---

## Status

- **Canon:** v0.9.8.4 (locked; corrections only by version
  increment per GR-1, ledger VL-007).
- **Build track:** G2 closed in code at VL-019. The G0 build
  track is the next active work, with the admissibility
  envelope (Deliverable 05) as the structural prerequisite.
- **Last ledger entry:** see `git log EVIDENCE/verification_ledger.md`.
