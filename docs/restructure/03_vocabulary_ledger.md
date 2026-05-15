# Elyon-Sol  -  Vocabulary Ledger

Every term used in Elyon-Sol's canon, code, and prose, mapped to the **exact code construct
it denotes**. Terms that map cleanly stay. Terms that do not are flagged: **DEFINE** (give it
a mechanism) or **CUT** (stop using it until/unless it has one).

---

## Terms that map cleanly to code  -  KEEP

| Term | Maps to | Notes |
|---|---|---|
| `AP` (Authority Provided) | `ctx["AP"]`, a list of strings | Concrete input field |
| `AR` (Authority Required) | `manifest["AR"]`, a list of strings | Concrete manifest field |
| `OP` (Operations Provided) | `ctx["OP"]`, a list of strings | Concrete input field |
| `R` (operations Required) | `manifest["R"]`, a list of strings | Concrete manifest field |
| AC^3 / Authority | `ac3_valid()` -> `AP_set >= AR_set` | Superset check. Maps cleanly. |
| T^26 / Coverage | `t26_valid()` -> `OP_set >= R_set` | Superset check. Maps cleanly. |
| CCS / Continuity | `ccs_valid()` | Boolean-identity + version + SHA256 match |
| G(I) | `evaluate()` | Conjunction of the three. Maps cleanly. |
| ELIGIBLE / REFUSE | return values of `evaluate()` | Terminal states. Concrete. |
| Fail-closed | the `except` and `None`-guard paths -> `REFUSE` | Real, demonstrable property |
| Deterministic | no randomness/state/time in `evaluate()` | Real property |
| Manifest | `MANIFEST/manifest.json`, validated by `safe_manifest()` | Concrete file |
| Manifest-bound | `manifest_sha256()` compared in `ccs_valid()` | Real property |
| Pre-execution | `evaluate()` runs before `requests.post` in `pep.py` | Real, with the bypass caveat |
| PEP (enforcement point) | `pep.py` `/governed-call` | Concrete, though "enforcement" is qualified  -  see below |

---

## Terms that DO NOT cleanly map  -  DEFINE or CUT

| Term | Problem | Recommendation |
|---|---|---|
| **"Substrate"** | Implies a foundational layer other things are built on. Currently there is nothing built on Elyon-Sol; it is a leaf, not a substrate. | **CUT** until something depends on it. "Gate" is the honest word. |
| **"Governance" / "AI Governance"** | The code checks set membership and hashes. It governs nothing the caller doesn't voluntarily route through it, and nothing about it is AI-specific. | **CUT** "AI." **DEFINE** "governance"  -  it currently means "admission control." Use "admission control" or "admission gate" until there is policy composition, delegation, or revocation. |
| **"Pre-governance"** | Undefined relationship to "governance." Prefix implies a stage before something that also isn't defined. | **CUT.** No code construct corresponds to it. |
| **"Canon"** | Acceptable as a name for the locked invariant set  -  *if* `CANON/canon.lock` makes "locked" checkable. As used in prose ("expanding canon," "canonical compression") it drifts into register without mechanism. | **DEFINE.** Canon = the contents of `CANON/canon.md`, hash-locked. Any sentence using "canon" must refer to that file or be cut. |
| **"Continuity Control Surface"** | "Surface" adds nothing over what `ccs_valid()` does. The function is three checks. | **DEFINE down** to "the continuity check" or keep CCS purely as the function name, not a conceptual object. |
| **"Operational realization"** | Prose phrase meaning "the tests passed." No construct. | **CUT.** Say "the test suite passes." |
| **"Admissibility"** | Acceptable  -  it names what `evaluate()` decides. But it must mean exactly "the ELIGIBLE/REFUSE decision," nothing larger. | **KEEP, bounded.** This is the right anchor term for the envelope. |
| **"Externally observable interception"** | Current proofs use a local second process or an ephemeral webhook. Neither is durable external verification. | **DEFINE.** Either build a persistent target-side log artifact, or downgrade the claim to "interception is observable at the PEP." |
| **"Mutation sensitivity"** | This one is *earned*  -  the `return True` corruption test genuinely demonstrates it. | **KEEP.** One of the few elevated terms the code backs. |
| **"Substrate state" / "pinned substrate state"** | Means "the manifest at a fixed hash." "Substrate" is doing decorative work. | **DEFINE down** to "the manifest at a pinned SHA256." |

---

## Rule going forward

A term is admissible in Elyon-Sol's prose if and only if a reviewer can point to the code
construct it denotes. The vocabulary ledger is itself a derivation-from-canon artifact: it
is how the project proves its language is bound to its mechanism. When the code grows, the
ledger grows with it  -  a term becomes usable the moment, and only the moment, its mechanism exists.
