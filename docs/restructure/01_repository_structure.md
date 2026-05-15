# Elyon-Sol  -  Repository Restructure Plan

**Status:** Proposal for review
**Premise:** Canon is locked. Everything else in the repository is *derivation from* canon. The repository  -  not any model's memory  -  is the continuity layer.

---

## Design principles

1. **Canon is the fixed point.** It is read-only in normal operation. Nothing else may contradict it; everything else must be traceable to it.
2. **Every claim has a location.** Description lives in one place, evidence in another, code in another. No claim exists in prose that is not backed by a file under `EVIDENCE/` or `TESTS/`.
3. **One source of truth per fact.** Test counts, version numbers, and the request schema each appear authoritatively in exactly one file. Everything else references it.
4. **Stale artifacts are removed, not left.** A proof describing an API the code no longer accepts is deleted or rewritten, never kept "for history" in a way that implies currency.
5. **The envelope is the bridge.** The admissibility envelope is the versioned object that proves derivation integrity holds as the manifest and implementation evolve beneath the locked canon.

---

## Proposed structure

```
Elyon-Sol/
+-- README.md                      # Entry point. Honest core description. Points to everything else.
|
+-- CANON/                         # LOCKED. The fixed point.
|   +-- canon.md                   # G(I) = Authority AND Coverage AND Continuity, invariants, lock statement
|   \-- canon.lock                 # hash of canon.md at lock time + version
|
+-- SPEC/                          # Derivation from canon. How canon becomes mechanism.
|   +-- admissibility_envelope.md  # The envelope: fields, hashing, versioning, reassertion protocol
|   +-- vocabulary.md              # Every term -> exact code construct it denotes
|   \-- request_schema.md          # THE authoritative request/response shape. Single source of truth.
|
+-- IMPLEMENTATION/
|   +-- evaluator.py               # The three-condition gate
|   +-- pep.py                     # HTTP enforcement layer
|   \-- envelope.py                # (future) envelope construction + reassertion
|
+-- MANIFEST/
|   \-- manifest.json              # AR, R, version
|
+-- TESTS/
|   +-- test_evaluator.py          # unit tests on the gate logic
|   +-- test_pep.py                # HTTP layer tests
|   +-- adversarial/               # adversarial suite  -  see 05
|   |   +-- test_mutation_sensitivity.py
|   |   +-- test_bypass.py
|   |   \-- test_boundary.py
|   \-- test_cases.json
|
+-- EVIDENCE/
|   +-- STATE.md                   # SINGLE SOURCE OF TRUTH: current commit, test count, what passes
|   +-- proofs/                    # each proof pinned to a commit hash, regenerable
|   \-- archive/                   # superseded proofs, clearly marked NON-CURRENT
|
\-- docs/
    \-- current_vs_claimed.md      # living gap document  -  see 04
```

---

## What moves, what changes, what is deleted

**Moves:**
- Existing `EVIDENCE/*.md` proofs -> either `EVIDENCE/proofs/` (if rewritten against current code) or `EVIDENCE/archive/` (if kept as history, clearly marked non-current).
- Evaluator and PEP stay in `IMPLEMENTATION/`  -  already correctly placed.

**Changes:**
- `README.md`  -  replace tagline-driven framing with the honest core description (Deliverable 02). The README currently says "3 passed"; it must reference `EVIDENCE/STATE.md` instead of hardcoding a count.
- Proof docs using the flat-key request shape (`interception_proof_001`, `_002`) are **stale**  -  they document an API `pep.py` no longer accepts. Rewrite against the nested `{target_url, context}` schema or archive them.

**Deleted / consolidated:**
- Any "operational state summary" prose that duplicates what STATE.md and the README should own. One description, one state file. Not a family of summary versions.

**New:**
- `CANON/canon.lock`  -  makes "locked" a checkable fact, not an assertion.
- `SPEC/`  -  the derivation layer. This is the part that currently exists only as prose scattered across summaries.
- `EVIDENCE/STATE.md`  -  kills the 3 / 30 / 34 / 37 contradiction permanently.
- `TESTS/adversarial/`  -  see Deliverable 05.

---

## Why this serves the stated objective

- **"Organization"**  -  every artifact has exactly one correct location and one job.
- **"Adversarial and external proofs"**  -  `TESTS/adversarial/` and `EVIDENCE/proofs/` are first-class, not afterthoughts.
- **"Assimilate everything into the core"**  -  `SPEC/` is where scattered prose becomes derivation; `CANON/` is the core it derives from.
- **"Declare it as what it should be"**  -  README + `current_vs_claimed.md` force the description to match the code.
- **"Envelope that can be reasserted for continuity"**  -  `SPEC/admissibility_envelope.md` + `IMPLEMENTATION/envelope.py` are the named home for exactly that.
- **Continuity without relying on a model**  -  any reviewer (Claude next session, Grok, you later) can orient from this tree alone.
