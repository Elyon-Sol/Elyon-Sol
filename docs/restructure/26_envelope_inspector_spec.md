# 26 - Envelope inspector / reconciler spec (VL-097)

Status: SINGLE-SOURCE (drafted in the VL-097 session from primary sources
`IMPLEMENTATION/envelope.py` and `IMPLEMENTATION/verifier.py`, re-read in
full this session per SESSION_PROTOCOL step 4 / VL-008 task-to-source
binding). Not yet cross-model-verified.

---

## 1. Purpose and honest scope

A LOCAL, read-only audit tool over signed admissibility envelopes. Four
capabilities, exactly the four named in STATE.md's Next-open-action
directive (chosen 2026-06-10):

1. **Inspect**: decode the exact scope a signed envelope binds - AP, OP,
   context, target_url, and the manifest version + sha pins - plus the
   issuance metadata (issuer_key_id, decision_id, not_after, decision,
   decision_sha256, canon/evaluator/manifest pins).
2. **Issuer verification**: verify the issuer signature against a pinned
   public key (the VL-040 signed region).
3. **Currency**: run `reassert()` for currency against live local state or
   a fetched published record (the VL-039 `record_source` seam).
4. **Reconcile**: given a log of EXECUTED actions and a log of ISSUED
   envelopes, classify every executed action. An action with no matching,
   bound, single-use envelope is an OUT-OF-SCOPE action. This is the
   auditability property worked out in the VL-096 follow-on discussion:
   issued envelopes are a complete, signed enumeration of everything that
   was authorized, so the executed-action log can be audited against them
   after the fact.

GR-3 honest scope: this is enabling / audit infrastructure and red-team
ergonomics, NOT a G5 closer. It introduces no new canonical invariant
(canon section 14), changes no production module, and has no caller on the
default pep.py path (build-then-wire discipline, parity with VL-074/076/078).
The reconciler audits a LOG; it does not observe execution itself. A target
that acts without logging, or logs falsely, is outside what any log audit
can establish - the trustworthy-log assumption is carried explicitly in the
module docstring and the report header.

## 2. Placement and integration boundary

- `IMPLEMENTATION/envelope_inspector.py` - the module + a small CLI.
- Imports FROM `envelope.py` (`reassert`, `canonical_json`,
  `_SIGNATURE_EXCLUDED_KEYS` - the one canonical definition of the signed
  region; importing it keeps the inspector incapable of diverging from
  `sign_envelope`'s region) and FROM `verifier.py` (the
  `REF_VERIFY_ENVELOPE_ABSENT` / `REF_VERIFY_SIGNATURE_*` vocabulary and
  the structural-guard key tuples). Nothing imports the inspector; the
  one-sided boundary (VL-025 pattern) holds.
- The inspector does NOT re-implement admission. Where it must apply the
  binding predicate (reconcile), it applies the same five comparisons
  `verify_envelope` step 3 applies (target_url string equality; AP/OP
  normalized-set equality; manifest-pinning string equality; context
  `canonical_json` equality), implemented against the same constants.

## 3. API

### 3.1 `inspect_envelope(envelope) -> dict`

Pure structural decode. Returns `{"ok": True, "scope": {...}, "meta": {...}}`
where `scope` carries exactly the bound fields (target_url, AP, OP, context,
expected_manifest_version, expected_manifest_sha256) and `meta` carries
decision, decision_sha256, canon/evaluator/manifest pins, envelope_version,
issuer_key_id, decision_id, not_after, timestamp_utc (None where absent).
A non-dict or an envelope failing the verifier's structural guard returns
`{"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}`. No signature, no
currency, no binding judgment - decode only, fail-closed on shape.

### 3.2 `verify_issuer(envelope, pinned_public_keys, now=None, clock_skew=timedelta(0)) -> dict`

The signature-and-window check ALONE (verifier steps 1.5 + 1.5b), with the
identical fail-closed semantics and codes (`REF_VERIFY_SIGNATURE_INVALID`,
`REF_VERIFY_SIGNATURE_UNKNOWN_KEY`, `REF_VERIFY_SIGNATURE_EXPIRED`), so an
auditor can attribute an envelope to an issuer without asserting currency
or binding. Returns `{"verified": bool, "reason": str}` with accept reason
`"ISSUER_VERIFIED"`. `pinned_public_keys` is required (the unsigned path is
not an audit path); `clock_skew` follows VL-075 (non-negative, ValueError
otherwise).

### 3.3 Currency

No wrapper. The inspector calls `envelope.reassert(envelope, record_source=...)`
directly (CLI `--record` flag loads a fetched-record JSON); the module
re-exports nothing. reassert()'s outcome vocabulary is already closed and
public.

### 3.4 `reconcile(executed_actions, issued_envelopes, pinned_public_keys=None, now=None, clock_skew=timedelta(0)) -> dict`

Inputs:

- `issued_envelopes`: list of envelope dicts as issued by the gate
  (signed; the gate's issuance log).
- `executed_actions`: list of action records, each
  `{"target_url": str, "interaction": {AP, OP, context,
  expected_manifest_version, expected_manifest_sha256},
  "decision_id": str | absent}` - the shape an enforcing target can record
  at the moment it acts (the reference target's `app.state.received`
  interaction, plus the target's own identity and the envelope's
  decision_id when it has one).

Classification (closed set, checked in this order per action, actions in
log order):

- `MATCHED` - a not-yet-consumed issued envelope exists whose decision is
  `"ELIGIBLE"`, whose binding predicate holds against the action
  (section 2), and - when the action carries a `decision_id` - whose
  `decision_id` equals it. The envelope is then CONSUMED (single-use,
  VL-066 exactly-once semantics).
- `DUPLICATE_CONSUMPTION` - every issued envelope that would otherwise
  match is already consumed by an earlier action. The log shows the same
  authorization honored twice: replay evidence at audit time.
- `OUT_OF_SCOPE` - no issued envelope matches at all (unattested or
  unauthorized execution; the A1-shaped event, visible only in audit).

Envelope-side findings:

- `UNUSED` - issued, valid, never consumed. Informational, not a
  violation (an authorization that was never exercised).
- `INVALID_ENVELOPE` - only when `pinned_public_keys` is supplied: an
  issued-log entry failing `verify_issuer` (or failing the structural
  guard, or whose decision is not `"ELIGIBLE"`) is excluded from matching
  and reported. A forged entry in the issuance log must not be able to
  legitimize an executed action.

Returns
`{"actions": [{"index", "verdict", "envelope_index" | None}],
"envelopes": [{"index", "status"}],
"summary": {"matched", "out_of_scope", "duplicate_consumption",
"unused", "invalid_envelopes", "clean": bool}}`
where `clean` is True iff out_of_scope == duplicate_consumption == 0.

Deliberate non-checks, recorded honestly: (a) reassert() currency is NOT
part of the matching predicate - at audit time the repository may have
legitimately transitioned since issuance, and a then-current envelope must
not be retro-invalidated by a later transition; currency at audit time is
capability 3, run separately when wanted. (b) `not_after` vs the action's
execution time is NOT checked - the action log records no timestamp in its
minimal shape; a deployment whose log carries timestamps can extend the
check (named as a future knob, not built). (c) The matcher is greedy in
log order; with single-use decision_ids (the gate's issuance behavior since
VL-066) greedy matching is exact, and for decision_id-less envelopes it is
deterministic and order-documented.

### 3.5 CLI

`python -m IMPLEMENTATION.envelope_inspector inspect <envelope.json>
[--keys <keys.json>] [--record <record.json>]` - prints the decoded scope;
with `--keys` ({key_id: ed25519_public_key_hex}) also the issuer verdict;
with `--record` (or by default, live local state) also the reassert outcome.
Exit 0 iff every check run passed.

`python -m IMPLEMENTATION.envelope_inspector reconcile --issued <issued.jsonl>
--executed <executed.jsonl> [--keys <keys.json>]` - prints the per-action
verdicts and the summary. Exit 0 iff `clean`.

JSONL: one JSON object per line; blank lines ignored. Key files map
key_id -> hex-encoded raw Ed25519 public key bytes; `cryptography` is
imported lazily ONLY when `--keys` / `pinned_public_keys`-from-file is used
(parity with envelope.py's no-hard-dependency rule).

## 4. Tests (canon- and spec-derived)

`TESTS/adversarial/test_envelope_inspector.py`, deriving from canon
sections 9 (fail-closed), 11.5/11.6 (AP/OP set semantics), 12-13 (currency
via reassert), 14 (non-executing, no new invariant), and this spec:
inspect decode + structural fail-closed; verify_issuer accept / tamper /
unknown-key / expired / skew; reconcile MATCHED / OUT_OF_SCOPE (no
envelope; binding mismatch on each of the five fields) /
DUPLICATE_CONSUMPTION (same decision_id twice) / UNUSED /
INVALID_ENVELOPE (forged issuance-log entry cannot legitimize an action) /
decision_id-priority matching / REFUSE-decision envelope never matches /
clean-flag semantics; CLI exit codes over tmp files.

## 5. Relation to the road

Artifact 13's road is complete in-house; G5 (a real EXTERNAL attacker on a
real PUBLIC surface) remains the only open road item and this increment
does not touch it. What this adds: when a live surface runs (the author's
deployments; an eventual public one), the gate's issuance log and the
target's action log become reconcilable artifacts - the red-team and the
reviewer get "every executed action maps to a signed, bound, single-use
authorization, or is named OUT_OF_SCOPE" as a checkable claim instead of
an assertion.
