# Adversarial review — Governance-layer design (Feature 1: human oversight / `PENDING_APPROVAL`)

**Reviewed against real source**, read from the git object store (`git show HEAD:…`, not the
truncating working-tree mount): `pep.py`, `evaluator.py`, `envelope.py`, `verifier.py`,
`replay_cache.py`, `executor_sdk.py`, `issuance_log.py`, `MANIFEST/manifest.json`.
Repo HEAD `dcc66dd` (design compiled against `c6b4094`, which is 1 commit behind HEAD — no
material drift). Design only; nothing built yet — no `approval.py`, no `HIGH_IMPACT`, and
`pep.py` holds **no replay/approval state today** (the gate is currently stateless). No code below.

Ranked by severity. Each item: the hole, *where exactly it fails to close in the real source*,
and the minimal design change.

---

## H1 — Missing/malformed `HIGH_IMPACT` silently disables the entire feature  *(Critical)*

**Hole.** `evaluator.safe_manifest()` validates only `AR`, `R`, `version` and returns the
manifest unchanged; it never looks at `HIGH_IMPACT`. If `requires_approval()` is written the
natural way — `manifest.get("HIGH_IMPACT", [])` — then a manifest with the key **missing,
typo'd, or wrong-typed** yields an empty high-impact set, so *nothing* is ever high-impact and
**every action forwards with no approval**. This is a silent, fail-*open* disabling of the whole
oversight guarantee, triggered by an ordinary config edit. It is the inverse of the manifest
discipline the codebase already keeps everywhere else.

**Where it fails to close.** `safe_manifest()` (evaluator.py L25-42) has no `HIGH_IMPACT` branch;
`evaluate()` calls `safe_manifest` then the three condition functions and returns ELIGIBLE without
ever consulting impact.

**Minimal change.** Make `HIGH_IMPACT` a *required, type-checked* manifest field inside
`safe_manifest()` (absence/malformation → `None` → `REFUSE`, exactly like `AR`/`R`). `requires_approval()`
must default to **True on any doubt** (no `.get(..., [])`). A manifest that cannot prove a key
is low-impact must treat it as high-impact. Add a revert-catcher: "manifest with `HIGH_IMPACT`
removed → high-impact call REFUSEs (or 202s), never forwards."

---

## H2 — The caller controls its own impact classification  *(Critical)*

**Hole.** `requires_approval(ctx, manifest)` reads the high-impact set from the pinned manifest
(good) but must *match* it against the operation/authority tokens in `ctx` — i.e. caller-asserted
`AP`/`OP`/`context`. Eligibility only forces the caller to declare the **required** tokens
(`t26_valid`: `OP ⊇ R`; `ac3_valid`: `AP ⊇ AR`). If a high-impact operation is keyed on a token
that is **not** in `R`/`AR`, the caller can simply omit/rename it: it escapes the `HIGH_IMPACT`
match, stays ELIGIBLE (the omitted token wasn't required), and executes with no approval. The
manifest is pinned, but the *selector* runs over caller input.

**Where it fails to close.** `ac3_valid`/`t26_valid` (evaluator.py) only enforce *superset* of
required tokens; they place no constraint on tokens outside `R`/`AR`. Any impact selector built
"the same way" inherits that gap.

**Minimal change.** Constrain `HIGH_IMPACT` to be expressed **only over tokens the caller is
already forced to declare truthfully** — i.e. require every high-impact selector token to be a
member of `R`/`AR` (so omitting it forces REFUSE), or derive impact from the gate-observed
`target_url`/operation rather than caller labels. State the residue honestly (per §1.9): a
benign-labelled call that is *semantically* high-impact is out of scope — impact is token-level,
not meaning-level.

---

## H3 — Single-use is the *only* thing bounding one-approval→one-execution, and it rests on machinery the gate doesn't have  *(Critical)*

**Hole.** Each approved resubmit mints a **new** signed envelope with a **new** `decision_id` and
a fresh 300 s window (`pep.py` ELIGIBLE branch). The target de-dups on `decision_id` — so
target-side replay defense will **not** catch a grant replayed at the gate (each forward carries a
different `decision_id`). The sole barrier between one human approval and *N* executions is the
gate consuming the grant exactly once. Three sub-failures:

1. **The gate is stateless today.** `pep.py` imports no replay cache and keeps no per-request
   state. Feature 1 introduces stateful single-use consumption into the gate *for the first
   time* — a brand-new failure domain the design treats as "reuse the existing replay_cache."
2. **R-02 multi-instance gap, inherited silently.** `replay_cache_from_env()` only fails closed
   on horizontal scaling if `ELYON_REPLAY_MULTI_INSTANCE=1` is *declared*; a multi-instance gate
   that forgets the flag gets per-process `InMemoryReplayCache`es that each honor the same grant
   once → *N* executions per approval. The design's "single-use via replay_cache" carries no
   honest-scope note about this.
3. **The "absent id → skip" guard.** `executor_sdk.check()` does
   `if decision_id is not None: check_and_claim(...)`. If grant single-use copies that pattern, a
   grant that simply **omits its id** skips the single-use check entirely → unbounded replay
   inside the freshness window.

**Minimal change.** (a) Grant single-use keyed on a **mandatory** `grant_id` — reject any grant
lacking it; never the `id is None → skip` pattern. (b) Require the **shared** cross-instance store
(`ExternalStoreReplayCache`) whenever the gate is multi-instance, reusing R-02's declare-or-fail
guard so a scaled gate cannot start with per-process caches. (c) Claim atomically *before* the
forward. (d) Add an honest-scope note: single-use holds only with a shared store under scale.

---

## H4 — `decision_sha256` is issuance-invariant, so binding to it does **not** bind to one request  *(High)*

**Hole.** By design (`envelope.py` `_HASH_EXCLUDED_KEYS`), `decision_sha256` excludes
`decision_id`, `not_after`, `timestamp_utc`, issuer fields — so two different issuances of the
*same* high-impact action (same `AP`/`OP`/`context`/`target_url`) produce an **identical**
`decision_sha256`. A grant bound to `decision_sha256` therefore authorizes **every** issuance of
that action, not one request. Single-request binding then rests *entirely* on `approval_request_id`
+ server-side pending-state — which the stateless gate does not keep. Without a tracked,
consume-once set of issued request-ids, any valid grant for action D can be reattached to a fresh
request for D and pass the binding check (because `decision_sha256` is equal).

Separately, §1.4's **"`decision_sha256` *or* the interaction content hash"** disjunction is a
latent hole: `target_url` is a **top-level** field, *not* part of `normalized_interaction`. It is
covered by `decision_sha256` but **not** by an "interaction content hash." Pick the wrong branch
and an approval for action-against-target-A is replayable against target-B.

**Where it closes / fails.** `decision_sha256` covers `request_context` (AP/OP/context/manifest
pins) **and** `target_url` (both inside the hashed region) — so *args/target* binding is fine **iff**
the grant binds `decision_sha256` specifically. Request *identity* is not in that hash at all.

**Minimal change.** Mandate binding to **`decision_sha256`** (drop the "or interaction hash"
branch and the redundant/possibly-nonexistent `context.args_sha256`). Add gate-side **pending-state**:
the 202 issues an `approval_request_id` into a server-side unconsumed set; on resubmit the gate
checks signature → `grant.decision_sha256 == recomputed decision_sha256 of *this* request` →
`grant.approval_request_id ∈ pending-and-unconsumed` → atomically consume. Request-binding lives in
that consumed-set, not in `decision_sha256`.

---

## H5 — Separation of duties is a string compare, not custody separation  *(High)*

**Hole.** `approver_key_id != gate_key_id` rejects only the trivial "same key id" case. It does
**not** prevent the gate from *minting its own approval* under a different key_id if the gate
process can reach the approver private key, nor if the gate controls the trust source that says
which approver key is authentic. The design's own words ("an approval the gate could mint itself
is not oversight") are not enforced by an id inequality.

**Where it fails to close.** `_get_signing_key()` resolves the gate key from injection/env. If the
approver key is resolvable the same way, the gate holds both. And the approver *public* key's
provenance is unspecified — a static/caller-supplied map lets a compromised gate swap in a key it
controls.

**Minimal change.** Two custody invariants: (1) the approver **private** key is *never* resolvable
by the gate process (mirror "never in the repo/env" — the gate holds only the approver **public**
key, for verification). (2) Approver-key provenance flows through the **existing signed
key-record / root-record chain** with an explicit `approver` role distinct from `issuer`; SoD is
enforced as **role-distinctness in the signed record**, not a key_id string. Add a proof that the
gate cannot read the approver private key.

---

## H6 — The 202 hold can be eaten by `pep.py`'s fail-closed catch, and fall-through reaches `requests.post`  *(Medium — and the core revert-catcher)*

**Hole.** The current ELIGIBLE branch wraps envelope-build + sign + issuance-log **and** the
upstream forward in broad `except Exception → REF_PEP_FAIL_CLOSED (403)`. If the
`PENDING_APPROVAL` hold is modeled as a raised signal *inside* that try, it is converted to a 403
(wrong terminal state, and it muddies the audit trail). And because `post_to_target(...)` is the
unconditional tail of the ELIGIBLE block, **any** path that doesn't explicitly divert will reach
the forward — exactly the ★ revert-catcher the design names.

**Where it fails to close.** `pep.py` ELIGIBLE branch: the `try: … sign … issuance_log.append …`
then `try: post_to_target …`. Nothing structurally prevents a fall-through.

**Minimal change.** Implement the high-impact gate as an explicit branch with its **own early
`return`** for the 202 path, placed **after** the ELIGIBLE check but **before** the sign/forward
try-block, so the hold is a normal response (not an exception) and the approved leg *falls through
to the existing single sign+forward* with no second forward. The TOCTOU answer: there is no
admit-then-revoke window **iff** the grant is consumed (claimed) atomically before `post_to_target`
and the 202/approved branches are mutually exclusive returns — make both explicit.

---

## H7 — Two freshness windows; grant freshness must reuse the proven primitive  *(Medium)*

**Hole.** The grant gets its own `not_after` (approval freshness) independent of the decision's
300 s window. `verify_envelope` already enforces decision `not_after` *correctly and fail-closed*:
naive (tz-less) `not_after` → `REF_VERIFY_SIGNATURE_EXPIRED`, strict `now >= not_after + skew` →
reject, with `clock_skew` handling. If grant freshness is **re-implemented** rather than reusing
that primitive, it will likely miss the naive-datetime fail-closed and the skew symmetry.
Secondary: consumption (claim) happens before the forward, so a forward that then fails leaves a
**consumed-but-not-executed** grant → the human must re-approve (availability edge, not a security
hole — worth an honest-scope line).

**Minimal change.** Grant freshness uses the **exact** `verify_envelope` checks (tz-aware
required, `current >= not_after + clock_skew` → REFUSE, same skew config). Document the
consumed-but-not-forwarded outcome as fail-closed-by-design (re-approval required).

---

## H8 — The governance claim is unprovable without held-request + grant-consumption in the reconciled log  *(Medium / audit)*

**Hole.** `issuance_log` records only **signed ELIGIBLE forwards**; `envelope_inspector reconcile`
checks executed-maps-to-issued. Feature 1's actual guarantee — *"no high-impact action forwarded
without a recorded human grant"* — has **no record to check** unless the held 202 and the grant
consumption are written to the *same* reconcilable log and a predicate ties them together.

**Where it fails to close.** `issuance_log.JsonlIssuanceLog.append(envelope)` takes only an
envelope; the reconcile spec has no notion of approval events.

**Minimal change.** Extend the issuance-log schema + `reconcile` with **approval-request** and
**grant-consumption** records, and add a predicate: *every forwarded high-impact `decision_id` has
a matching consumed-grant record bound to its `decision_sha256`.* That predicate **is** the
auditable governance trail; without it the §1.6 claim is asserted, not proven.

---

## Cross-cutting notes

- **Build order is right.** Feature 1's *mechanism* is isolatable, but per the design's own §1.9,
  its *guarantee* is void until Feature 2 (non-bypassable) lands — a caller that skips the gate
  skips the human. Don't let any readiness predicate flip to green on Feature 1 alone.
- **The gate becomes stateful.** H3/H4 both stem from this. The single biggest architectural
  shift Feature 1 introduces is moving the gate from stateless to stateful (pending-set + grant
  replay cache). Treat that state store with the same fail-closed, shared-under-scale discipline
  as the executor replay cache, or the oversight guarantee degrades silently under horizontal
  scaling.
- **Honest-scope additions needed:** multi-instance single-use (H3), token-level vs semantic
  impact (H2), consumed-but-not-forwarded (H7).
