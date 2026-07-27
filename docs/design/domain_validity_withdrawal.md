# The domain-validity (D) layer: built, then withdrawn

**2026-07-27.** A record of a direction taken and reversed, kept because a mistake found and
removed is worth more than a mistake erased — provided it is stated.

This is a design-decision record, not a verification event. Per GR-4 it is **not** a ledger
entry: nothing here is a claim verified against a primary source except the security finding in
§3, which is recorded with its referent. Per GR-3 the comparative judgments in §2 are model
evaluative output and are **not** evidence.

---

## 1. What was built

A domain-semantic validity layer intended to expand the invariant set to
`G(I) = AC³ ∧ T²⁶ ∧ CCS ∧ D(I, domain)` — the gate answering not only *"is this authorized?"*
but *"is the content this authorized call carries valid for its declared domain?"*

Delivered in full over roughly two days:

- **`domain_validity.py`** — a deterministic predicate evaluator over the interaction's content,
  dotted-path addressed, recursing into nested objects; closed rule vocabulary of five
  (`present` / `absent` / `equals` / `in` / `not_in`); type-strict; fail-closed.
- **`domain_verdict.py`** — a signed out-of-band policy attestation (SAFE / UNSAFE) bound to the
  decision hash and domain, freshness-windowed, single-use.
- **`domain_control.py`** — a four-state machine: PASS / HOLD_FOR_VERDICT / HOLD_FOR_HIL / REFUSE,
  pure with respect to its inputs (the verdict is passed in, never fetched — a determinism firewall).
- **`domain_authority.py`** — a third trust role resolved from the signed key-record chain,
  structurally disjoint from `issuer` and `approver`, so a policy authority could attest but never
  mint or approve.
- A hash-pinned domain ruleset, an attested human-override path, and **168 tests** (suite 645 → 813).

The engineering was competent and the discipline held. **The frozen core was never touched:**
`evaluator.py`, `MANIFEST/manifest.json`, `EVIDENCE/published_hashes.json` and `CANON/*` are
byte-identical across the entire attempt. No canon-version event occurred. Build-then-wire and
the GR-1 boundary survived under pressure — the process worked even where the judgment did not.

## 2. Why it was withdrawn

Not because it was broken. Because it was **the wrong shape for the thesis**.

- **It competed where the project loses.** A five-predicate vocabulary is a poor duplicate of
  OPA, Rego and Cedar — and directly contradicts the project's own stated position that it
  *composes with* policy engines rather than replacing them.
- **Its strongest claimed distinction was prior art.** "Strict post-authorization structural
  refuse" — named by two independent reviewers as the most defensible differentiator — is
  Gatekeeper and Kyverno since 2019, and Kubernetes VAP+CEL since 2024.
- **The claimed advantage was inflated.** An in-session estimate of "+7" separation against
  comparable stacks did not survive adversarial analysis, which returned **+1 to +2 in novelty
  and 0 deployed**. The inflation was model-authored and repeated after a first correction; that
  is precisely the failure mode GR-3 exists to prevent, and it was not caught by the discipline.
- **Nothing consumed it.** Absent from every runbook, compose file, Dockerfile and env example,
  from the README, from `EVIDENCE/readiness.json`, and from both the ext-authz sidecar and the
  MCP server — i.e. absent from the surface `deploy/NONBYPASS_TOPOLOGY.md` designates as
  non-bypassable. Built capability; zero deployed capability.
- **More surface meant more holes** — see §3.

The governing judgment: **an admission gate that starts inspecting content is on its way to
becoming a policy engine.** Every additional plane of competition is additional surface to
defend, and the thesis — deterministic, fail-closed, pre-execution admissibility — is stronger
narrow than broad.

## 3. The security finding (the part worth keeping)

**An authentication bypass was introduced by the new layer and shipped publicly before being
found.** Recorded here in full because it is the most transferable thing the attempt produced.

**The defect.** The human-override path let a grant name, inside its signed region, the UNSAFE
verdict it overruled — and waived that verdict's freshness window, because human re-determination
outlives a verdict's lifetime. The override id was read from an **unsigned** request header,
deliberately, since the grant is verified later. A code comment asserted this was safe because
"the release itself still requires that grant to verify."

**Why that reasoning failed.** It holds for an UNSAFE verdict, which can only be released through
the approval block. It does **not** hold for a SAFE verdict, which PASSes straight to forward and
never reaches grant verification. So a captured, authority-signed SAFE verdict that had expired
arbitrarily long ago could be revived by appending a header the attacker wrote themselves.

**Referent — reproduced by execution against the running gate**, with the upstream forward
instrumented:

| Input | Result |
|---|---|
| expired SAFE verdict alone | `202` held, upstream **not** called ✓ |
| + unsigned `{"overrides_verdict_id": …}` | `200`, upstream **CALLED** ✗ |
| repeated | `200`, upstream **CALLED** again ✗ |

Freshness and single-use both defeated, with no signing key and no valid grant. The layer's own
**168 tests did not catch it.** It was found by adversarial review, not by the suite.

**Lessons, in order of transferability:**

1. **A confident comment explaining why something is safe is exactly where to look for the case
   it does not cover.** The comment was specific, reasoned, and wrong in one branch.
2. **Author-written tests do not substitute for adversarial review.** 168 tests, written by the
   same mind that wrote the defect, missed a bypass reachable from an unsigned header.
3. **Reading unverified input "just to route" is still trusting it.** The value was used before
   verification on a path where verification never arrived.
4. **New surface is new attack surface.** The bypass existed only in the newest, least-reviewed
   code, on the flagship feature.

## 4. What was kept

Two changes made during the attempt were **independent defects** and survive the revert:

- `SPEC/request_schema.md` now documents `interaction_type`, an OPTIONAL field the validator has
  accepted since the typed-impact increment but which was never specified — pre-existing
  claim-vs-code debt.
- `site/index.html` no longer advertises a **live** public break-it challenge as a differentiator
  while simultaneously stating the public nodes were retired on 2026-07-20. It was
  self-contradictory in three places and the break definitions named hostnames that no longer
  resolve.

## 5. Standing position

`G(I) = AC³ ∧ T²⁶ ∧ CCS`. Unchanged, and not expanding. The direction is depth on the surfaces
that already exist — not new planes of competition. G5 (external adversarial validation) remains
NOT-MET, and no capability added or removed here changes that.
