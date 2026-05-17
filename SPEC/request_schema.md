# Elyon-Sol - Request Schema (Draft)

**Status:** Draft for review. Derivation from locked canon v0.9.8.4
section 11 (Formal Interaction Model) with cross-references to
section 12 (Continuity) and section 13 (Evaluation Function).
**Build-order position:** Step 1 of
`docs/restructure/05_admissibility_envelope_spec.md`. This artifact
locks the request shape; the admissibility envelope embeds it.
**Gap coverage:** Anchor artifact for G2 (request schema drift -
interception proofs document a dead API). Referenced by G10
(documentation requirement for load-bearing caller-asserted fields).

---

## What this artifact is

A specification of the request shape that `IMPLEMENTATION/pep.py`
accepts. The shape is derived from the canonical formal interaction
model (section 11), not retrofitted from the current code. Where canon
and code diverge, this artifact names the divergence rather than
papering over it.

A request that does not conform to this schema is REFUSED at the PEP
boundary, with a refusal reason. Schema conformance is a precondition
of evaluation, not part of evaluation.

## What this artifact is not

- Not a description of the wire format alone. The wire format is one
  rendering of the shape; the shape is canonical.
- Not a description of the admissibility envelope. The envelope is a
  decision artifact (return value); this is a request artifact
  (input). The two are distinct.
- Not a description of internal evaluator state. The evaluator's
  `manifest`, `result`, `decision_sha256`, etc., are not part of the
  request.

---

## Canon mapping - section 11 -> request fields

Direct mapping from the canonical interaction tuple to fields the
caller must supply. The canon name in the left column is authoritative;
the schema name in the right column is the on-the-wire form used in
this repository.

| Canon (section 11) | Meaning | Schema field | Required? |
|---|---|---|---|
| `I` (section 11.1) | the interaction itself | the entire `interaction` object | yes |
| `A` (section 11.1) | actors | implicit in `AP` (section 11.5); caller need not name actors separately | n/a |
| `S` (section 11.1) | system state | not caller-supplied; system property | n/a |
| `C` (section 11.1) | context | `interaction.context` | yes |
| `t` (section 11.1) | time | not caller-supplied; PEP records receipt timestamp | n/a |
| `AP(I)` (section 11.5) | present authorities | `interaction.AP` | yes |
| `OP(I)` (section 11.6) | observed coverage | `interaction.OP` | yes |
| `AR(I)` (section 11.3) | required authorities | NOT caller-supplied; derived from manifest `M` per section 11.9 | n/a |
| `R(I)` (section 11.4) | coverage requirements | NOT caller-supplied; derived from manifest `M` per section 11.9 | n/a |

`AR(I)` and `R(I)` come from the manifest, not the request. The caller
asserts what they bring (`AP`, `OP`); the manifest defines what is
required. This split is load-bearing: a caller cannot weaken `AR` or
`R` by sending different values, because they are not in the request.

## Canon mapping - section 11.9 -> manifest-pinning fields

Section 11.9 requires the manifest to be deterministic, versioned, and
integrity-verifiable. To preserve fail-closed semantics under manifest
drift, the request asserts which manifest the caller intended.

| Canon basis | Schema field | Required? | Semantics |
|---|---|---|---|
| section 11.9 ("deterministic, versioned, and integrity-verifiable") | `expected_manifest_version` | yes | caller-asserted; compared by string equality against `manifest.version` |
| section 11.9 + section 12.4 (manifest version change is an invalid transition) | `expected_manifest_sha256` | yes | caller-asserted; compared against the live manifest hash |

Both fields are CALLER-ASSERTED. The caller is naming the manifest
they reasoned against. If the live manifest does not match, the gate
REFUSES, per VL-012's documented convention for load-bearing pinning
fields. This convention is the resolution of G10.

A request with these fields absent is REFUSED at the schema boundary
(see "PEP boundary behavior" below). A request with these fields
present but disagreeing with the live manifest is REFUSED inside
`evaluate()` via `manifest_integrity_valid()`.

## Canon mapping - section 12 -> not in request

CCS (section 12) is a property of the transition `S_t -> S_{t+1}`,
not of a single request. No request field implements or asserts CCS.
A caller cannot supply CCS state; it is derived by the gate (and,
per G0 build track, will be derived via the admissibility envelope's
reassertion protocol - see Deliverable 05).

The previously-present caller-asserted `ccs_valid` field was REMOVED
in VL-012 (commit `8ba88cf`) as part of the G0/G6/G10 disambiguation
pass. The schema reserves the name "CCS" for the canonical section-12
invariant only; no request field uses it.

---

## Schema

### Top-level wire shape

The PEP accepts a single object at `POST /governed-call`:

```
{
  "target_url":   "<string, RFC 3986 absolute URL>",
  "interaction": {
    "AP":                         [<string>, ...],
    "OP":                         [<string>, ...],
    "context":                    {<canon C, free-form key/value>},
    "expected_manifest_version":  "<string>",
    "expected_manifest_sha256":   "<64-char lowercase hex string>"
  }
}
```

`target_url` is a PEP-wire concern, not part of canonical `I`. It
addresses the upstream the PEP forwards to on ELIGIBLE. It is OUTSIDE
the interaction object so that the canonical mapping in the table
above is preserved exactly.

### Field-by-field

#### `target_url` (string, required)

The absolute URL the PEP will forward the request to if and only if
the decision is ELIGIBLE. Not derived from canon. Not included in the
data the evaluator sees. Not part of any hash. Validated as a
syntactically well-formed absolute URL; the PEP performs no semantic
validation of the target.

#### `interaction.AP` (array of strings, required)

Present authorities. Section 11.5. Set semantics: order is not
significant; duplicates are coalesced; the empty array is valid (and
will fail AC^3 against any non-empty `AR`).

Element type: string. Element values are caller-defined symbols
(e.g., `"identity"`, `"role"`); their meaning is defined by the
manifest's `AR` for the relevant interaction class. The schema does
not constrain the symbols themselves.

#### `interaction.OP` (array of strings, required)

Observed coverage. Section 11.6. Same set semantics and element rules
as `AP`. Evaluated against `R` per section 11.8.

#### `interaction.context` (object, required)

Canonical `C` (section 11.1). Free-form key/value object carrying
interaction context that is not authority and not coverage but is
material to whether the interaction should occur. Section 12.1 names
context as one of the four things whose change constitutes a state
transition; this field is the canonical carrier of that material.

The schema does not constrain the keys or values inside `context`.
Manifest schemas for specific interaction classes may. Required as a
field (must be present); MAY be the empty object `{}` if no context
applies.

NAMING NOTE: this field is named `context` to mirror canon section 11.1.
It is NOT the same as the outer `context` field in the pre-schema PEP
(`pep.py` at HEAD), which is a flat bag holding `AP`, `OP`, and pinning
fields. This schema replaces that flat bag. Migration is part of the
G2 closure work described under "PEP boundary behavior."

#### `interaction.expected_manifest_version` (string, required)

Caller-asserted manifest version. Compared by string equality against
`manifest.version` inside `manifest_integrity_valid()`
(IMPLEMENTATION/evaluator.py). Caller-assertion semantics per VL-012;
canon basis: section 11.9 + section 12.4.

#### `interaction.expected_manifest_sha256` (string, required)

Caller-asserted manifest hash. 64-character lowercase hex string.
Compared against the live SHA256 of `MANIFEST/manifest.json` inside
`manifest_integrity_valid()`. Caller-assertion semantics per VL-012;
canon basis: section 11.9 + section 12.4.

NOTE (G11): at HEAD, `manifest_sha256()` reads the manifest from a
hardcoded path rather than hashing the manifest argument that
`evaluate()` was called with. This is asymmetric with how the manifest
itself is passed in. The asymmetry is bookkeeping-batch (G11); it does
not affect this schema, but the schema's `expected_manifest_sha256`
semantics will become tighter once G11 is resolved.

---

## Rejected shapes (G2 closure)

The following shapes are explicitly REFUSED at the PEP boundary.

### Flat-key payload (archived interception proofs)

`EVIDENCE/archive/interception_proof_001.md` and `_002.md` document a
request shape with `AP`, `OP`, and other fields at the TOP LEVEL of the
JSON object rather than nested under `interaction`. That shape is
REFUSED. The interception proofs are archived for exactly this reason
(G2). Refusal reason code: `REF_SCHEMA_FLAT_KEYS`.

A request with `AP` or `OP` at the top level is treated as
schema-malformed regardless of any other fields present. The PEP does
not attempt to lift the fields into a synthetic `interaction` object.

### Missing manifest pinning

A request whose `interaction` object lacks
`expected_manifest_version` or `expected_manifest_sha256` is REFUSED.
Refusal reason code: `REF_SCHEMA_MANIFEST_PINNING_MISSING`.

The caller-assertion convention (VL-012) means that "no assertion" is
treated as schema-malformed, not as "any manifest will do." The
fail-closed posture (section 1, section 9) requires the caller to name
the manifest they reasoned against.

### Authority/coverage of wrong type

`AP` or `OP` present but not an array of strings (e.g., a string, a
nested object, an array of mixed types). REFUSED. Refusal reason
code: `REF_SCHEMA_TYPE_MISMATCH`.

This is a strictness boundary, not a canon requirement per se. Canon
section 11.5/11.6 defines `AP` and `OP` as sets; this schema
operationalizes "set" as "deduplicated array of strings" on the wire.

### CCS-shaped fields

Any field whose key contains the substring `ccs` (case-insensitive) or
makes a continuity assertion (e.g., a `prior_state_hash`,
`continuity_token`, `ccs_valid`). REFUSED. Refusal reason code:
`REF_SCHEMA_RESERVED_CCS`.

VL-012 reserves "CCS" for the canonical section-12 invariant only.
Caller cannot assert CCS; the gate derives it. The G0 build track is
where the gate gains that capability. Until then, the gate REFUSES
caller attempts to assert it - this is stricter than the current
code, which would silently accept unknown keys inside `context`. The
strictness is intentional: silent acceptance is the surface that let
G6 live undetected.

---

## PEP boundary behavior

The PEP performs schema validation BEFORE calling `evaluate()`. The
order is load-bearing:

1. Parse JSON. Failure -> REFUSE with `REF_SCHEMA_PARSE_ERROR`.
2. Top-level shape: `target_url` and `interaction` both present and of
   correct type. Failure -> REFUSE with `REF_SCHEMA_TOP_LEVEL`.
3. `target_url` is a syntactically valid absolute URL. Failure ->
   REFUSE with `REF_SCHEMA_BAD_URL`.
4. `interaction` contains exactly the required fields named above; no
   unknown top-level keys inside `interaction`; no flat-key
   collisions (G2). Failure -> REFUSE with appropriate code from
   "Rejected shapes."
5. Field types match the table above. Failure -> REFUSE with
   `REF_SCHEMA_TYPE_MISMATCH`.
6. Only after all of the above: `evaluate(interaction, manifest)` is
   called.

Schema-layer refusals MUST NOT call `evaluate()`. Schema-layer
refusals MUST NOT forward to `target_url`. Both prohibitions follow
from the fail-closed posture (section 9): an unevaluatable request is
a refused request, and the upstream is never called on REFUSE.

The current `IMPLEMENTATION/pep.py` performs none of this validation;
it accepts `context: Dict[str, Any]` opaquely and lets `evaluate()`
fail closed on whatever shape arrives. Closing G2 requires:

- moving schema enforcement to the PEP boundary,
- updating `pep.py` to construct the `interaction` it passes to
  `evaluate()` only after schema checks pass,
- adding refusal-reason-code emission at the schema layer matching the
  codes named above,
- the in-place rename from `pep.py`'s outer `context` to `interaction`
  (canon-faithful name) and the introduction of `interaction.context`
  for canonical `C`.

These code changes are downstream of this artifact. This artifact
locks the target shape.

---

## Relationship to other artifacts

- **Locked canon (`CANON/canon.md`).** Sections 11, 12, 13 are the
  derivation source. Section 11.9's "deterministic, versioned, and
  integrity-verifiable" is the load-bearing clause for the pinning
  fields.
- **Admissibility envelope spec
  (`docs/restructure/05_admissibility_envelope_spec.md`).** The
  envelope's `request_context` block embeds the shape defined here.
  When the envelope is built, the embedded shape is exactly the
  `interaction` object specified above.
- **Manifest (`MANIFEST/manifest.json`).** The manifest's `version`
  field is what `expected_manifest_version` is compared against. The
  manifest's SHA256 is what `expected_manifest_sha256` is compared
  against (modulo G11).
- **PEP (`IMPLEMENTATION/pep.py`).** Receives the request. Today it
  does no schema validation; closing G2 moves the validation into the
  PEP boundary, as described in "PEP boundary behavior."
- **Evaluator (`IMPLEMENTATION/evaluator.py`).** Receives the
  interaction object after schema validation. Performs AC^3, T^26,
  and `manifest_integrity_valid()` (VL-012). Does NOT perform schema
  validation; that is the PEP's job per the layering above.
- **Archived interception proofs (`EVIDENCE/archive/`).** Documented
  the flat-key shape this schema rejects. They are archived under G2;
  the rejection rules in "Rejected shapes" are what makes them
  permanently retired rather than merely stale.
- **Maintenance protocol (`docs/MAINTENANCE_PROTOCOL.md`).** This
  artifact, once committed, is corrected by version increment per
  GR-1's spirit if the canon-derived mapping changes. In-place
  edits are permitted for derivation-faithful refinements that do
  not change the wire shape.

---

## Open questions for review

1. **Strictness on unknown keys inside `interaction.context`.** This
   draft does not constrain keys inside `context`. Manifest schemas
   for specific interaction classes might. Should there be a
   default-deny or default-allow posture at the schema layer for
   unknown context keys? Default-deny is more fail-closed but
   front-loads manifest schema work; default-allow defers strictness
   to the manifest. Recommend default-allow at the schema layer,
   default-deny at the manifest layer, with manifest schema work
   tracked as a separate gap. Confirm.
2. **Versioning of this schema.** The envelope has
   `envelope_version: "1.0"`. Should the request shape also carry a
   `schema_version`? Argument for: makes the wire format
   evolution-safe. Argument against: every wire-level surface
   becoming version-tagged is bookkeeping creep. Recommend NO field;
   schema is versioned by git commit of this artifact and by the
   admissibility envelope's `envelope_version`. Confirm.
3. **`AP` and `OP` as sorted on the wire.** Set semantics say order
   does not matter. For canonical JSON serialization in the envelope,
   order will need to be canonical (sorted). Should this schema
   require callers to sort, or should the PEP normalize before
   embedding in the envelope? Recommend PEP normalizes; callers
   should not have to know about envelope serialization. Confirm.
4. **`target_url` allowlist.** Should `target_url` be constrained
   to a manifest-derived allowlist of upstreams? This is a G4
   (bypassability) concern; this artifact does not resolve it.
   Flagged here so that if it gets added later, the change is
   localized to `target_url`'s rules above.
---

## Decided downstream tasks

The following are not open questions; they are decisions that
schedule downstream work outside this artifact's scope.

### Feed-back to envelope spec (Deliverable 05)

Artifact 05's `request_context` block (under "Envelope structure")
names four fields: `AP`, `OP`, `expected_manifest_version`,
`expected_manifest_sha256`. This schema specifies that the request
also carries `context` (canon's `C`, section 11.1) and a PEP-wire
`target_url`. The envelope should reflect the full canonical shape it
embeds: option (a) - artifact 05's `request_context` block grows a
`context` field mirroring canon section 11.1, and the envelope grows
a sibling `target_url` field at top level (the envelope is a decision
artifact; the target the decision was about IS part of the decision's
audit trail).

This is a freshness-pass-class edit to artifact 05, scheduled AFTER
this schema is committed and reviewed. Same shape as VL-013's
freshness pass on artifacts 05 and 06: the artifacts' substantive
content is preserved; only statements about current state that became
stale (in this case, the post-this-schema state of the `interaction`
shape the envelope embeds) get touched. The pass will:

- add `context: {...}` to the envelope-structure JSON block, placed
  inside `request_context` between `OP` and `expected_manifest_version`,
  with a comment citing canon section 11.1 and this schema as derivation;
- add `target_url: "..."` at envelope top level, between `decision`
  and `canon`, with a comment citing this schema's `target_url`
  rules (G4 deferral noted);
- append a field-rationale bullet for each of the two new fields,
  matching the prose style of the existing bullets;
- record the pass in the ledger as a separate entry (proposed
  VL-018, after the VL-014..VL-017 schema-work entries below).

No code change in artifact 05's pass; no canon change; no test
change. Same scope rule as VL-013.

---

## Build order (schema-internal)

This is the order to implement the schema work after this artifact
is committed. Each step is committable as a unit.

1. Commit this artifact.
2. Add `TESTS/adversarial/test_request_schema.py` with one test per
   rejected shape in "Rejected shapes," plus positive cases that
   round-trip valid requests. These tests MUST fail against the
   current `pep.py` (which accepts everything) - that failure is
   the honest G2 signal, same shape as G7's canon-derived tests
   that must fail until the envelope lands.
3. Add a schema validator module (suggested:
   `IMPLEMENTATION/request_validator.py`) implementing the boundary
   behavior in the order specified.
4. Wire `pep.py` to call the validator before `evaluate()`. Rename
   the outer `context` to `interaction` at this step. This is the
   commit where G2 closes in code.
5. Update `EVIDENCE/archive/interception_proof_001.md` and `_002.md`
   to cite this schema as the artifact that retires them (additive
   to their existing NON-CURRENT headers). Note: pre-existing
   non-ASCII bytes in those files (VL-011 process finding) remain
   open and are not addressed in step 5.
6. Freshness pass on `docs/restructure/05_admissibility_envelope_spec.md`
   per "Decided downstream tasks" above: add `context` to the
   envelope's `request_context` block, add `target_url` at envelope
   top level, with rationale bullets. No code change.

Steps 2-4 are the code-side of G2. Step 1 is this artifact alone.
Step 6 reconciles the envelope spec to this schema. Each step gets
its own ledger entry: VL-014 (this artifact), VL-015 (failing
tests), VL-016 (validator), VL-017 (PEP wiring + G2 close), VL-018
(artifact 05 freshness pass).
This split is per VL-011's lesson that distinct concerns get distinct
commits, not bundled commits whose diffs muddy each other.

---

## What this artifact does NOT close

- **G0 build track.** The schema does not implement CCS. It reserves
  the name and refuses caller attempts to assert it, but the
  canonical section-12 invariant requires the admissibility envelope
  (Deliverable 05), not just a schema.
- **G7.** Canon-derived tests for AC^3, T^26, and CCS are separate
  from the schema-shape tests proposed in step 2 above. Schema tests
  check shape; canon-derived tests check invariants. Both are
  needed; this artifact addresses neither directly.
- **G11.** The manifest-source asymmetry in `manifest_sha256()` is
  noted under `expected_manifest_sha256` but not resolved here.
  Bookkeeping batch.
- **G4.** Non-bypassability of the gate is out of scope; the schema
  defines what the PEP accepts but not how upstreams might require
  the PEP's involvement.

These are intentionally left open. The schema is one unit of forward
motion; conflating it with other gaps is what STATE.md's "smallest
unit of forward motion that unblocks multiple downstream items"
language was warning against.
