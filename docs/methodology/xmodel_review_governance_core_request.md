# Cross-Model White-Box Adversarial Review — Governance Core (independent run)

> Provide this prompt **plus the source files listed under "Sources"** to the model (Grok and
> OpenAI each get an independent run). Do NOT provide any prior reviewer's findings. The goal is an
> independent pass whose convergence with other runs is measured afterward — so this prompt names
> the properties to test but not the answers.

## Scope binding — this defines a VALID run (read first)
Your review must rest ONLY on the source files provided below. Specifically:
- **Cite real `path:line` for every claim.** If you cannot point at a line in the provided sources,
  do not assert the behavior. A run that cites a file or line not in scope, or asserts a behavior
  without a citation, is **discarded** (this project discards fabricated-citation runs).
- **Do not rely on memory of any prior version of this project**, or on any other repository. Reason
  only from the bytes in front of you.
- **End your response with one line** confirming you stayed within the provided sources and cited
  only them.

## The system (neutral)
This is a deterministic, fail-closed HTTP admission gate (a PEP). A governance layer adds
human-in-the-loop approval for "high-impact" actions: when the manifest classifies an admitted call
as high-impact, the gate must HOLD it and not execute it until a human approver, using a key that is
not the gate's, produces a signed "approval grant"; the gate verifies that grant, consumes it once,
and only then forwards the call upstream. The design and its review fixes are in
`docs/design/governance_layer_design.md` (the code refers to them as `[FIX H1]`–`[FIX H8]`).

## Your task
Adversarially review the governance layer for ways to violate the security properties below. For
each property, try to **construct** a concrete input, message interleaving, or deployment
configuration that breaks it. If you cannot break it, say what you tried and why it held (negative
results are wanted). For each finding, state whether it is **exploitable as written** (on a correct,
single-process deployment) or **deployment-gated** (only under a stated misconfiguration / scaling
condition). This is a white-box review — you have the source — so it is internal hardening evidence,
**not** a claim of external validation; do not describe it as the latter.

A standing question throughout: **does each of `[FIX H1]`–`[FIX H8]` actually hold in the code, or
only in its docstring?**

## Sources (review ONLY these + their direct callees)
- `docs/design/governance_layer_design.md`  (the spec + the 8 fixes)
- `IMPLEMENTATION/approval.py`               (build/sign/verify the approval grant)
- `IMPLEMENTATION/approver_trust.py`         (resolve which public keys may authorize)
- `IMPLEMENTATION/key_record_source.py`      (the signed key-record chain)
- `IMPLEMENTATION/impact.py`                 (high-impact classification)
- `IMPLEMENTATION/pending_store.py`          (the held-request set)
- `IMPLEMENTATION/replay_cache.py`           (single-use claim)
- `IMPLEMENTATION/pep.py`                     (the request handler that wires the above + forwards)
- `IMPLEMENTATION/approver_cli.py`           (the human approver surface)
- `IMPLEMENTATION/issuance_log.py`, `IMPLEMENTATION/envelope_inspector.py`  (audit / reconciliation)
- `IMPLEMENTATION/governance_wiring.py`      (startup wiring guard)
- For reference only (what the project claims is covered — look for gaps between these and reality):
  `TESTS/adversarial/test_approval.py`, `test_approval_audit.py`, `test_requires_approval.py`,
  `test_approver_trust.py`, `test_pending_store.py`, `test_governance_wiring.py`,
  `TESTS/test_pep_approval.py`, `TESTS/test_governance_integration.py`.

## Properties to break
- **P1 — the forward gate.** Is there ANY path by which a high-impact action reaches the upstream
  forward without a valid, fresh, single-use human grant?
- **P2 — binding.** A grant authorizes exactly the action and the one held request it was minted
  for. Can a grant release a different action, different arguments, a different target, or a
  different held request?
- **P3 — separation of duties.** The party that runs the gate cannot produce an approval the gate
  will honor. Is that enforced by something the gate operator cannot forge, or only by a comparison
  the operator controls? Consider every way the gate can be configured to decide which keys it trusts.
- **P4 — single-use under concurrency and scale.** Trace "approved" → "executed." Under threads,
  multiple worker processes, and multiple replicas — with and without a shared store — can one
  approval cause more than one execution? Where exactly-once degrades, is the degradation
  fail-closed, fail-open, or silent?
- **P5 — freshness + fail-closed defaults.** Expired / malformed / missing freshness or policy —
  does it fail closed (require a human / refuse) or open? Is the default (non-high-impact) path
  unchanged?
- **P6 — audit.** Could you forward an approved high-impact action while leaving no auditable record
  tying it to a grant? Under what configuration?

## Where to look hardest (open questions — find your own answers)
- Across the *different ways the gate can be configured to trust approver keys*, are all paths
  equally safe, or is one weaker than another? What is the weakest configuration an operator could
  pick, and what does it permit?
- In `verify_grant`, in what order are the checks applied, and is every check it appears to make
  actually load-bearing in the way `pep.py` calls it — or is any of them redundant / vacuous given
  how the arguments are supplied?
- Walk every store backend (in-memory, external/shared, the Redis variants) and every deployment
  shape (one process, N workers, N replicas, shared store present/absent, declared/undeclared).
  Build a small table of where exactly-once holds and where it does not, and classify each gap.
- Which governance guarantees are *opt-in* (depend on an env var / a wiring step being present), and
  what happens to the guarantee if an operator omits that step while still enabling high-impact
  actions? Is the omission caught loudly, caught quietly, or not caught?
- Compare the tests to the code: is there a property the design claims that no test actually
  exercises, or a test that passes for a reason other than the one it names?

## Output format (per finding)
```
[your-id]  short title
Class:    EXPLOITABLE AS WRITTEN | DEPLOYMENT-GATED | RULED OUT
Severity: Critical | High | Medium | Low
Property: P1..P6
Where:    path:line (must be real and in scope)
Repro:    the concrete input / interleaving / config that triggers it
Why:      1–2 sentences
Fix:      the minimal change
```
Then: a summary table; a list of "properties I could NOT break, and what I tried"; an `[FIX H1]`–
`[H8]` holds-in-code table; and the scope-confirmation line.

## Rules recap
Cite real in-scope `path:line`. No fabrication. Distinguish exploitable-now from deployment-gated.
Treat the design doc as the spec. Do not claim external validation. Prefer constructing the break
over asserting it.
