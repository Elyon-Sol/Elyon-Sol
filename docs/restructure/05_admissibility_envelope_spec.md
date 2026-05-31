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
  "target_url": "<URL the decision was about; see SPEC/request_schema.md target_url rules; G4 deferral noted>",
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
    "context": {"<arbitrary caller-supplied object; canon section 11.1 `C`; SPEC/request_schema.md `interaction.context` is derivation>": "..."},
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
  "decision_sha256": "<hash over canonicalized envelope minus this field, timestamp_utc, and (signed path) issuer_key_id + issuer_signature>",
  "issuer_key_id": "<gate public-key id; present and REQUIRED on the signed path; inside the signed region>",
  "issuer_signature": "<Ed25519 sig over canonical(envelope minus issuer_signature and timestamp_utc); signed path only; excluded from its own region; absent on the unsigned path>",
  "timestamp_utc": "2026-05-14T00:00:00Z"
}
```

### Field rationale

- **`target_url`**  -  the URL the decision was about, recorded as part of the audit trail.
  Derived from `SPEC/request_schema.md`'s `target_url` rules (HTTPS-only at the schema layer;
  see G4 deferral on non-bypassable enforcement). Including the target in the envelope makes
  the decision auditable on its own: a reader of a persisted envelope knows what the gate
  decided about, not only what the gate decided. Participates in `decision_sha256` by the
  default rule (only `timestamp_utc` is excluded).
- **`canon` block**  -  pins the decision to the locked canon (whitepaper version + hash). If
  `CANON/canon.lock` ever shows a different hash, every prior envelope provably predates a
  canon change. This makes "canon is locked" *enforceable*, not merely stated.
- **`evaluated_against`**  -  the manifest state, per section 11.9 ("the manifest must be
  deterministic, versioned, and integrity-verifiable").
- **`request_context.context`**  -  the caller-supplied `C` from the canonical interaction
  tuple `I = (A, S, C, t)` (canon section 11.1). Required by the request schema
  (`SPEC/request_schema.md` makes `interaction.context` required at the wire boundary; that
  decision is the schema-layer half of G12). Recording `context` in the envelope preserves
  the inputs that produced the decision; this is the same discipline as recording `AP` and
  `OP`. Members of `request_context` are not individually enumerated as bullets here; this
  bullet exists because `context` is the load-bearing addition from the VL-014..VL-019
  schema work.
- **`evaluator` block**  -  pins to the implementation. A changed evaluator hash means the
  decision logic itself moved (section 12.4-class transition).
- **`condition_results`**  -  note the explicit split. `manifest_integrity` is the point-in-time
  check, implemented in `IMPLEMENTATION/evaluator.py` as `manifest_integrity_valid()` (renamed
  from `ccs_valid` in VL-012; closes the rename half of G0 and resolves G6). `ccs` is the
  **true section 12 invariant**  -  decision consistency across a transition  -  and is only
  meaningfully evaluable at *reassertion* time, because it is inherently about `S_t -> S_{t+1}`.
  Implementing it is the G0 build track (open).
- **`decision_sha256`**  -  tamper-evidence. Canonical JSON (sorted keys, no whitespace,
  `ensure_ascii=True` per VL-009 ASCII-safe standard), reusing the serialization
  discipline from the existing replay-receipt work (note: `IMPLEMENTATION/replay/receipt.py`
  currently uses `ensure_ascii=False`; the divergence is recorded as a methodology-debt
  finding at VL-012 and reinforced at VL-025). On the signed path, `decision_sha256` is
  computed over the canonical envelope minus `decision_sha256`, `timestamp_utc`,
  `issuer_key_id`, and `issuer_signature`, so it is identical signed-vs-unsigned and
  `reassert()` Row 2 verifies a signed envelope unchanged; the issuer fields' integrity
  is the signature's responsibility, not `decision_sha256`'s.
- **`timestamp_utc`**  -  audit only; **excluded** from `decision_sha256` so the same decision
  is bit-identical regardless of issue time (preserves section 9 reproducibility).
- **`issuer_key_id`** (signed path)  -  identifies the gate public key the target uses to
  verify `issuer_signature`; enables key rotation. Inside the signed region (it is part of
  what `issuer_signature` covers), so it cannot be swapped to point at a different pinned
  key without breaking the signature. Required whenever an envelope is signed.
- **`issuer_signature`** (signed path)  -  an Ed25519 signature (via the `cryptography`
  library) over `canonical_json(envelope minus issuer_signature and timestamp_utc)`  -  the
  same exclusion discipline as `decision_sha256`, applied to the signature itself. It
  authenticates the *issuer* (the gate) of the decision artifact: it proves the envelope
  was minted by the holder of the gate's private key, which a recomputed `decision_sha256`
  cannot (that hash is unkeyed and reproducible by anyone  -  the VL-039 follow-up 2 forgery
  finding). Absent on the unsigned path. See "Issuer signature (opt-in)" below.

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
| `decision_sha256` does not verify | `INVALIDATED` | sections 12.3/12.4 fail-closed semantics, operationalized via artifact-05-layer tamper detection |
| `evaluator_sha256` != live evaluator hash | `RE-EVALUATE-REQUIRED` | section 12.4  -  decision logic transition |
| `manifest_sha256` != live manifest hash | `RE-EVALUATE-REQUIRED` | section 7/section 12.4  -  manifest version/schema transition |
| all hashes match AND `decision_sha256` verifies | `REASSERTED` | section 12.3  -  continuity holds; `d_{t+1} = d_t` provably |

`reassert()` is **pure with respect to the envelope**: it reads live file hashes
(`canon.lock`, `IMPLEMENTATION/evaluator.py`, the live manifest) but does not modify
its input envelope. Callers may pass a persisted envelope to `reassert()` and rely on
the envelope's bytes remaining unchanged.

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

## Issuer signature (opt-in)  -  VL-040

Closes the VL-039 follow-up 2 forgery finding: `decision_sha256` is an unkeyed hash
over the envelope's own public fields, so a party who knows the published record can
mint a from-scratch envelope that `verify_envelope` accepts. The envelope is
tamper-evident, not forgery-resistant. A signature authenticates the issuer.

- **Mechanism.** The gate signs each envelope with an Ed25519 private key (the
  `cryptography` library). The target verifies `issuer_signature` against a pinned
  public key selected by `issuer_key_id`. The signed region is
  `canonical_json(envelope minus issuer_signature and timestamp_utc)`, so the signature
  covers `decision_sha256` and `issuer_key_id`.
- **Opt-in.** Unsigned envelopes remain valid; signing is a capability
  (`sign_envelope(envelope, signing_key, key_id)` plus
  `verify_envelope(..., pinned_public_keys=...)`). The default path is byte-unchanged
  and the existing suite is preserved. Forgery is closed only on the signed path  -
  stated, not blanket; the mandatory cutover is a named follow-on.
- **Key model.** The private key is never in the repository. The target holds the
  pinned public key, distributed out-of-band exactly as `IMPLEMENTATION/published_source.py`
  distributes the record anchor (Decision B-prime-1). Trust does not vanish; it moves to
  public-key distribution plus the `issuer_key_id` -> key map. Said plainly, the same
  honesty as the pinned anchor.
- **Layering (no new reassertion row).** Signature verification is a verifier-layer
  concern (`IMPLEMENTATION/verifier.py`; artifact 08), NOT a `reassert()` / CCS concern.
  CCS currency (does live state still match the envelope's pins?) and issuer provenance
  (did the gate mint this?) are orthogonal axes. The reassertion-protocol table is
  unchanged; `decision_sha256`'s region excludes the issuer fields so a signed envelope
  passes Row 2 unchanged.
- **Fail-closed (canon section 9).** A missing, malformed, or invalid signature, or an
  unknown / unpinned `issuer_key_id`, is a REFUSE on the signature-required path  -  never
  a pass-through and never a silent downgrade to the unsigned path. Reason codes:
  `REF_VERIFY_SIGNATURE_INVALID` (missing / malformed / verification-failed) and
  `REF_VERIFY_SIGNATURE_UNKNOWN_KEY` (key id not in the pinned set).
- **Canon basis (no new invariant).** Signing operationalizes section 8.2 (PoE: an
  optional, implementation-dependent integrity anchor that "does not affect admissibility
  logic") and extends the section 11.9 integrity-verifiability that already justifies
  `decision_sha256`. Admissibility (AC^3 AND T^26 AND CCS) is untouched. Section 14
  (identity-agnostic) holds: the key proves who ISSUED the attestation, not who the
  actors are  -  actor authority is still evaluated only via the manifest.
- **Claim-track gate.** The word "forgery-resistant" does not enter any citable claim,
  and no Zenodo deposit is made, until the key-governance cross-model evaluate has run
  (key distribution, rotation, compromise, revocation). Build fast, claim slow.

---

## Open questions for review

1. **`ccs` field on first issuance and at reassertion (resolved at VL-026).** On the
   initial decision there is no `S_t`  -  only `S_{t+1}`  -  and canon section 12.3 is
   inapplicable (it presupposes a transition). `build_envelope()` records
   `condition_results.ccs` as Python `None` (JSON `null`) on first issuance; the
   `"INITIAL"` sentinel proposed in Rev. 2 was rejected in favor of `None` for Python/JSON
   convention and to keep the type signature `Optional[bool]`. At reassertion,
   `reassert()` derives `condition_results.ccs` from the row outcome: `True` on
   `REASSERTED` (the canon's `d_{t+1} = u_{t+1} AND c_{t+1}` holds per row 5);
   `False` on any `INVALIDATED` or `RE-EVALUATE-REQUIRED` outcome (continuity does not
   hold; per section 12.4 "if any condition is violated: CCS = 0"). The derivation
   is `reassert()`'s output, not stored back into the envelope (envelope purity per
   the contract above). Implementation note: envelope.py at VL-025 returns the row
   outcome only; the ccs-derivation rule named here is a forward-looking spec
   statement that VL-026 tests will assert against and that a small envelope.py
   update (deferred to VL-027 or earlier) will satisfy.
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
