# Elyon-Sol  -  Current State vs. Claimed State (Rev. 2)

A living document. Left: what the code does, verified against `evaluator.py`, `pep.py`,
`manifest.json`, `test_pep.py`, and the v0.9.8.4 canonical whitepaper. Right: the delta
and the required action.

**Rev. 2 changes:** Added **G0** (CCS spec/implementation drift) as the anchor gap.
Corrected G1 (overstated in Rev. 1). Re-grounded all rows against the now-available canon.

This document's job is to be **uncomfortable and accurate**. A row closes only when code,
tests, or structure change such that the delta no longer exists  -  never by editing prose.

---

## G0  -  CCS specification/implementation drift  *(ANCHOR GAP)*

- **Canon (whitepaper section 12):** CCS is a **temporal invariant over state transitions**  -
  `CCS(S_t, S_{t+1}, I)`. It requires authority transitions justified by AC^3, coverage
  transitions justified by T^26, and decision consistency `d_{t+1} = u_{t+1} AND c_{t+1}` across
  `S_t -> S_{t+1}`. section 13: "Eligibility does not persist across state transitions without
  revalidation." section 7/section 12.4 list invalid transitions: manifest version change, role/authority
  schema change, identity mapping inconsistency.
- **Code (`ccs_valid()`):** A **point-in-time** check  -  `ccs_valid is True`, version-string
  match, manifest SHA256 match. No `S_t`, no `S_{t+1}`, no prior state, no transition concept.
- **Delta:** The implemented CCS and the canonical CCS are **not the same invariant**. The
  code implements something closer to whitepaper section 8.1 "manifest-bound authority" than to
  section 12 CCS. **Confirmed cause: drift**  -  `ccs_valid()` was built without section 12's transition
  semantics in view; the shared name (input field `ccs_valid`, function `ccs_valid()`,
  invariant CCS) masked the gap; tests were written against the code, not the canon, so
  green tests created false confidence.
- **Status: RESOLVED** (VL-029) - rename half closed (VL-012); build half closed (VL-029).
- **Action:**
  1. Rename the implemented check to its true scope (e.g. `manifest_integrity_valid()`).
     **DONE under VL-012.**
  2. **Reserve** the name "CCS"  -  unused in code  -  until section 12 is implemented.
     **DONE under VL-012**; reservation extended to test IDs.
  3. Implement section 12 transition logic via the admissibility envelope (see Deliverable 05).
     **DONE under VL-029** (envelope.py with build_envelope() and reassert() landed at VL-025; ccs-derivation rule landed at VL-029; pep.py wires envelope emission on ELIGIBLE at VL-029).
  4. Add canon-derived tests for section 12 (see G7).
     **DONE under VL-034** (envelope domain canon-derived via test_ccs_canonical.py at VL-028; evaluator domain canon-derived via test_evaluator_canonical.py at VL-034).
  5. Until step 3 lands, the project must claim only "manifest integrity is enforced," **not**
     "CCS is implemented." **RESOLVED at VL-029** - step 3 landed; the project may now claim "canonical CCS is implemented at the envelope layer" (G7 fully closed at VL-034 with evaluator-domain canon-derived tests).

---

## Open gaps

### G1  -  README test count is stale  *(downgraded from Rev. 1)*
- **Code:** `test_pep.py` contains **4** tests (refuse-blocks-upstream, eligible-forwards-once,
  upstream-error-fails-closed, version-drift-refuses).
- **Claimed:** README says "Expected: 3 passed."
- **Delta:** README undercounts its own primary test file. The 30/34/37 figures in evidence
  docs are *plausibly* the same growing suite at different commits  -  not necessarily
  contradictory  -  but there is no commit-pinned source of truth.
- **Correction note:** Rev. 1 framed this as a credibility crisis across four contradictory
  numbers. That was overstated. The real issue is narrower: no single source of truth, and a
  stale README.
- **Action:** Create `EVIDENCE/STATE.md` pinned to a commit hash as the only authoritative
  count. README references it; hardcodes nothing.
- **Status: RESOLVED** (VL-052) - the count-discipline is on disk: `README.md` hardcodes
  no test counts and pins `STATE.md` (under "Current verified state") plus the latest
  `VL-NNN` ledger entry as the authoritative count for the current commit (verified
  VL-050 finding 3). The Action's literal path was `EVIDENCE/STATE.md`; the count source
  landed as root-level `STATE.md`, which satisfies the "README references it, hardcodes
  nothing" criterion.

### G2  -  Request schema drift
- **Code:** `pep.py` accepts `{target_url, context: {...}}` (nested). Confirmed by
  `test_pep.py`, which posts exactly that shape.
- **Claimed:** `interception_proof_001.md` / `_002.md` send flat top-level `AP`/`OP`.
- **Delta:** Those two proofs document an API the code rejects.
- **Action:** Rewrite both against the nested schema or move to `EVIDENCE/archive/` marked
  NON-CURRENT. `SPEC/request_schema.md` becomes the single source of truth. Per G10, the
  schema must also document the `version` field's caller-assertion semantics.
- **Status: RESOLVED** (VL-014 + VL-015 + VL-016 schema track + VL-017 failing schema-shape tests + VL-018 `IMPLEMENTATION/request_validator.py` + VL-019 PEP wiring). `SPEC/request_schema.md` is the single source of truth and the validator is wired into `pep.py` (the interception proofs were archived NON-CURRENT). The G12/G13 canon-layer halves remain OPEN (see below). STATE.md and the priority order agree.

### G3  -  Framing vs. mechanism  *(re-grounded against canon)*
- **Canon:** The whitepaper is a legitimate formal specification  -  formal interaction model,
  set-theoretic invariant definitions, explicit scope/non-goals, and a correct "Relation to
  Prior Work" section (RBAC/ABAC/XACML/UCON/reference monitor). The *specification* earns
  serious vocabulary.
- **Code:** Faithfully implements AC^3 and T^26. **Partially** implements CCS (see G0). Does
  not implement the section 4/section 15 failure constructs (CDD/SAP/PAD/ILT)  -  but the canon says those
  "do not participate in admissibility determination," so that is consistent, not a gap.
- **Delta:** The gap is **not** "prose oversells a toy." It is narrower and more precise: the
  *implementation* under-implements the *specification* on CCS, and the public framing claims
  the whole canon is realized. Rev. 1's "validator with delusions of grandeur" framing was
  wrong and is retracted.
- **Status: RESOLVED** (VL-030) - README rewrite at VL-029 follow-up (`5f833fb`); Zenodo addendum Revision 2 (DOI `10.5281/zenodo.20387278`) published; enforcement evidence at `EVIDENCE/proofs/g3_enforcement_evidence_001.{log,md}`.
- **Action:** Reframe public materials as "a formal admissibility specification (v0.9.8.4)
  with a faithful partial implementation." Use Deliverable 06 to state exactly which
  invariants are FULL / PARTIAL / DRIFTED. Apply the vocabulary ledger. **DONE under VL-030.**

### G4  -  Bypassability
- **Code:** `pep.py` forwards via plain `requests.post`. The target cannot verify a call
  came through the gate.
- **Canon:** section 14 says Elyon-Sol "operates pre-execution" and "governs legitimacy." section 2 calls
  it a "non-executing governance substrate." The canon does not explicitly claim
  non-bypassability  -  but a reader reasonably infers enforcement.
- **Delta:** The gate is opt-in. A caller can hit the target directly and bypass it.
- **Action:** State the property plainly in README now. Add `TESTS/adversarial/test_bypass.py`
  demonstrating the bypass honestly. Schedule non-bypassable enforcement in build-outward
  scope; note the envelope-on-forwarded-call thread (Deliverable 05, open question 3).
- **Status:** design landed at VL-036 (`docs/restructure/08_enforcement_design.md`); build pending VL-037. G4 NOT resolved (a design artifact does not close a build-outward gap); moves from open-undesigned to open-designed. E1: G5 (durable published hash source) named as the verification precondition. Recommended VL-037 increment: delivery-agnostic target-side verifier reusing `reassert()` plus a `request_context`-vs-live-interaction binding check; A1 (declining caller) named as closeable only by target-side policy, not by the gate.
- **VL-037 (build, increment 1):** `IMPLEMENTATION/verifier.py` `verify_envelope()` landed. It is a delivery-agnostic target-side verifier reusing `reassert()` (currency plus integrity; closes forgery A2) plus a symmetric `request_context`/`target_url` binding check (closes same-state replay A3 per artifact 08 section 7). Canon-derived tests at `TESTS/adversarial/test_verifier.py`; honest A1-bypass demonstration at `TESTS/adversarial/test_bypass.py` (the Action item, done). Delivery wiring pending VL-038. **G4 enforcement status unchanged**: the verifier has no caller yet, so the opt-in delta above still holds, and G4 does NOT transition to RESOLVED. G5 remains the named deployment precondition; A1 remains closeable only by a target-side policy, not by the gate.
- **VL-038 (build, increment 2):** delivery landed and G4 is now enforced for routed traffic. `pep.py` PUSHES the envelope on the ELIGIBLE forward as the out-of-band header `X-Elyon-Sol-Envelope` (canonical JSON; forwarded body unchanged, so a routed call and a direct call differ only by the header). An enforcing target (`TESTS/adversarial/test_enforcement.py`) verifies a delivered envelope against the committed published record `EVIDENCE/published_hashes.json` (the Decision-C anchor: the published hashes, not the target's local disk), reusing `verify_envelope()` as-is for `decision_sha256` integrity (A2) plus `request_context`/`target_url` binding (A3). Refused-bypass evidence at `EVIDENCE/proofs/g4_refused_bypass_001.{log,md}`: one routed call honored and acted; five refused (403, not acted)  -  direct/no-envelope (A1), forged (A2), replayed and target_url-mismatch (A3 binding), and an envelope whose pins do not match the published record (the defensibility case  -  it passes local-disk `reassert()` and binding yet is refused on the published record). **G4 is now defensibly non-bypassable for routed-and-attested traffic; it does NOT transition to blanket RESOLVED:** A1 (the declining caller) remains closeable only by a target-side admission policy, and cross-host TRANSPORT of the published record (the target fetching it rather than holding a committed local copy) remains the G5 hardening, named not built (artifact 08 sections 4.4 / 6).
- **VL-040 (issuer signing, opt-in):** the VL-037/VL-038 treatment closed the TAMPER sub-case of A2 (a mutated envelope fails `decision_sha256` / `reassert()` Row 2) but NOT the FORGERY sub-case: `decision_sha256` is unkeyed, so a party who knows the published record can mint a from-scratch envelope with a correct `decision_sha256` and no signature (VL-039 follow-up 2; the envelope is tamper-evident, not forgery-resistant). Issuer signing closes the forgery sub-case on the SIGNED path: `build_envelope()` output is signed by `sign_envelope()` (Ed25519) and an enforcing target verifies `issuer_signature` against a pinned public key before `reassert()` (`REF_VERIFY_SIGNATURE_INVALID` / `REF_VERIFY_SIGNATURE_UNKNOWN_KEY`, fail-closed). Opt-in: `pep.py`'s default forward stays unsigned and the existing suite is byte-unchanged; forgery is closed only where signing is required; the mandatory cutover is the named follow-on. Trust moves to issuer-public-key distribution (parallel to the B-prime-1 anchor). Tests `TESTS/adversarial/test_signing.py`; evidence `EVIDENCE/proofs/signing_forgery_defeated_001.{log,md}`. "Forgery-resistant" is not a settled claim pending the key-governance cross-model evaluate. Spec: artifact 05 "Issuer signature (opt-in)" (VL-040).
- **VL-041 (issuer-key expiry, opt-in):** `sign_envelope(envelope, signing_key, key_id, not_after=...)` stamps a tz-aware `not_after` INSIDE the signed region (covered by `issuer_signature`, so a captured signed envelope's window cannot be extended) and OUTSIDE `decision_sha256` (`_HASH_EXCLUDED_KEYS`, so a signed-with-expiry envelope's `decision_sha256` is byte-identical to the unsigned one and `reassert()` Row 2 is unchanged); `verify_envelope(..., now=...)` enforces `now < not_after` at Step 1.5b, fail-closed to `REF_VERIFY_SIGNATURE_EXPIRED` (canon section 9). Time-bounds an UNDETECTED issuer-key compromise WITHOUT depending on detecting the leak; does NOT close revocation (the detected-compromise case) and does NOT touch the trust root. Tests `TESTS/adversarial/test_signing_expiry.py` (11); proof `EVIDENCE/proofs/signing_expiry_001_runner.py` (exit 0). Canon 8.2/9/11.9; no new invariant; section 14 holds (the window bounds the ISSUER's attestation, not actor identity). Build-then-wire: no `pep.py` change. Spec `abdb9e0`; build `807ccfe`. Suite 149 -> 160 + 0 xfailed. "Forgery-resistant" stays BOUNDED.
- **VL-042 (published signed key record / revocation, opt-in; B-prime-2):** `EVIDENCE/published_keys_gen.py` (live signer; the record is a runtime artifact, never committed  -  artifact 09 custody) + `IMPLEMENTATION/key_record_source.py` (new reader, mirrors `published_source.py` as a sibling: pinned-root signature -> freshness -> per-key trust view; emits `REF_VERIFY_KEY_RECORD_INVALID` / `REF_VERIFY_KEY_RECORD_STALE`) + `verify_envelope(..., key_record_view=...)` record-exclusive lookup (`REF_VERIFY_KEY_UNKNOWN` / `REF_VERIFY_KEY_REVOKED` / `REF_VERIFY_KEY_OUT_OF_WINDOW`) before the unchanged signature + VL-041 expiry checks. Closes the DETECTED-compromise instant-kill case (revocation) that expiry could not reach, and relocates trust from N per-issuer pins to ONE pinned publisher/root key  -  a NEW, singular, load-bearing trust floor (root compromise is total). Tests `TESTS/adversarial/test_key_record.py` (15); proof `EVIDENCE/proofs/key_record_001_runner.py` (exit 0). First `IMPLEMENTATION/` module to import `cryptography` (envelope/verifier stay duck-typed). Canon 8.2/9/11.9/13; no new invariant; section 14 under the narrowed reading (the root is THE trusted identity). Build-then-wire: no `pep.py` change. Spec `c323b65`; build `5e9fbf6`. Suite 160 -> 175 + 0 xfailed. The publisher/root key OWES its own framework-level evaluate (VL-042 follow-up); "forgery-resistant" stays BOUNDED, out of any deposit.
- **VL-043 (readiness instrument; not a capability move):** the WIRING-track drift gate (artifact 10) adds the third axis beyond CAPABILITY and CLAIM. `EVIDENCE/readiness.json` (the single source of readiness truth: per-capability `built` / `wired_to_default` / `exercised_e2e` / `transported`, each test-backed-or-false-with-reason) + `IMPLEMENTATION/readiness.py` (engine) + `TESTS/readiness/test_readiness.py` (fails the build on a dishonest manifest) + `TESTS/readiness/test_deployment_predicates.py` (the three predicates as declared xfail). It adds NOTHING to the admission path (no `verifier.py` / `evaluate()` / canon change; no new invariant). Honest initial state: 0 of 3 deployment predicates green BY DESIGN  -  DEFAULT_SECURE (the G4 mandatory signing cutover; the canary `test_unsigned_path_unchanged_forge_still_accepted` flips it), END_TO_END_NO_SHORTCUT (G5 cross-host transport), and ROOT_RECOVERY (VL-044 rotation wired to `pep.py`'s default path + transported) are all RED. VL-041/042/044 advanced CAPABILITY, not deployment; the gate exists so the green capability track cannot mask the red wiring track. Spec `efeb8ba`; build `753e978`. No follow-up evaluate (it makes no claim about the world). GR-rule candidate for `MAINTENANCE_PROTOCOL.md`.
- **VL-044 (planned root rotation + per-root status, opt-in; B-prime-3):** a current root signs its successor's designation, so a target pinning only R1 trusts a designated R2 IN-BAND (transitive root trust, bounded by status + freshness, conservative single hop); per-root status (active/retired/revoked) gates the SIGNING root at the record-validation layer. `EVIDENCE/published_roots_gen.py` + `IMPLEMENTATION/root_record_source.py` (sibling reader -> per-root status view) + a `root_status_view` gate on `key_record_source.py` (`REF_VERIFY_ROOT_REVOKED`; `REF_VERIFY_ROOT_RETIRED` via `issued_at < retired_at`; `root_status_view=None` = VL-042 byte-behavior) + four `REF_VERIFY_ROOT_*` constants in `verifier.py` (NO `verify_envelope` logic change). Tests `TESTS/adversarial/test_root_record.py` (18); proof `EVIDENCE/proofs/root_record_001_runner.{py,log}` (live R1->R2 rotation, exit 0). The honest ceiling: root-key COMPROMISE recovery is irreducibly out-of-band; only PLANNED rotation is built. Canon 8.2/9/11.9/13/14; no new invariant; section 14 narrowed reading one layer up (rotation MOVES the trusted identity, does not ADD identity to the admission path). Build-then-wire: no `pep.py` change. Spec `7cfc699` + conservative-frame `9e5181b`; build `aec58ee`. Suite 178 -> 196 + 3 xfailed. The transitive-designation cross-model evaluate (VL-044 follow-up; Grok/OpenAI/Gemini, blind, off-record) returned SOUND 3-0: transitive designation adds NO adversary reach beyond the VL-042-follow-up root-compromise-is-total bound, so "forgery-resistant" is UNMOVED. Two deferred gap candidates (retirement clock-skew, load-bearing; consumer-layer window enforcement, minor) are folded into the artifact-11 spec pass (VL-045 commit 2).
- **VL-061 / VL-063 (the two named G4 preconditions now BUILT; status still not blanket RESOLVED):** the deployable reference enforcing target (`IMPLEMENTATION/reference_target.py`, VL-061) is a real target-side admission policy. Configured entirely from out-of-band pins, it fails closed per request on an absent envelope (A1 -> `REF_VERIFY_ENVELOPE_ABSENT`), a keyless-forged or tampered signed envelope (A2; the pinned gate key makes the signature REQUIRED -> `REF_VERIFY_SIGNATURE_INVALID`), a replay or `target_url` swap (A3 binding -> `REF_VERIFY_BINDING_MISMATCH`), and an unconfigured / anchor-mismatched record (`REF_TARGET_NOT_CONFIGURED` / `REF_TARGET_ANCHOR_MISMATCH`). So A1  -  which every prior increment named closeable ONLY by a target-side policy, not by the gate  -  is now closed for any target that adopts this reference policy; the target supersedes the `target.py` stub (removed at VL-068). VL-063 builds the second named precondition: gate / reference target / publisher run as three separate OS processes over real CA-verified TLS (artifact 12 steps 2-3, single-host in-env), so cross-host TRANSPORT of the published record is no longer modeled (capture/redeliver). **G4 still does NOT flip to blanket RESOLVED:** both preconditions are built only at single-host fidelity with no EXTERNAL attacker; a non-adopting target or a declining caller can still bypass; and finish line (B)  -  an external attacker on a real surface  -  is what certifies it (GR-3; artifact 12 section 1).

### G5  -  "External" verification is not durable
- **Code/evidence:** Interception proofs rely on a local process (`127.0.0.1:9000`) or an
  ephemeral, now-dead `webhook.site` URL.
- **Claimed:** "Externally verified interception."
- **Delta:** Neither is a persistent, reproducible, third-party artifact.
- **Action:** Build a target-side logging receiver; commit its log to `EVIDENCE/proofs/`.
  Until then, downgrade the claim to "observable at the PEP."
- **VL-038 (partial):** `EVIDENCE/published_hashes.json` is committed  -  a persistent, hash-locked, third-party-checkable artifact extending `CANON/canon.lock`'s discipline to the evaluator and manifest hashes, derived live by `EVIDENCE/published_hashes_gen.py` (never hand-copied). The G4 refused-bypass evidence (`EVIDENCE/proofs/g4_refused_bypass_001.{log,md}`) anchors every verdict to this committed record, so a third party can re-derive the verdict by cloning the repository  -  the durable, reproducible artifact G5 calls for. G5 is NOT closed: the target still reads the published record from a committed local copy; cross-host TRANSPORT (the target fetching it from a canonical published location, so a target on a different host need not trust its own files) remains the open hardening. `reassert()` still reads local disk; co-located that agrees with the published record, and the published-record check is what carries defensibility.
- **VL-039 (transport built):** cross-host transport of the published record landed. `IMPLEMENTATION/published_source.py` lets a target fetch the published record over loopback HTTP and verify it against a single pinned root anchor (the sha256 of `EVIDENCE/published_hashes.json`, derived live, held out-of-band; Decision B-prime-1). Per Decision D-b, `envelope.reassert()` and `verifier.verify_envelope()` gained an optional `record_source` parameter (local-disk default preserves the co-located path and the 131 baseline); when supplied, the currency check consults the fetched record, not local disk (Decision C). Evidence at `EVIDENCE/proofs/g5_cross_host_001.{log,md}`: a target in a genuinely byte-mutated tree HONORS a valid envelope via the fetched authentic record DESPITE its divergent local disk (a VL-038-style local-disk verify would have returned RE-EVALUATE-REQUIRED), and still REFUSES a forged envelope, a record failing the pinned anchor, and an un-attested call. Tests at `TESTS/adversarial/test_cross_host.py`. G5 moves from open-with-committed-record to transport-built; trust is bootstrapped at one pinned anchor. G5 does NOT become blanket RESOLVED: anchor distribution, record freshness/revocation, signing/PKI, and true multi-machine/TLS remain the G5 floor (named, not built; Decision F).
- **VL-042 / VL-044 (G5 transport surface):** the B-prime-2 key record (`key_record_source.fetch_key_record`) and the B-prime-3 root record (`root_record_source`) are fetched over loopback HTTP  -  the same transport model as B-prime-1's `published_source.py` (VL-039)  -  so cross-host TRANSPORT of the key/root records is part of the open G5 floor (true multi-machine + TLS named, not built). Each record carries its own freshness bound (`not_after`) so a cached record fails closed in the interim. G5 unchanged: transport remains a loopback wrapper; the END_TO_END_NO_SHORTCUT readiness predicate stays RED until real cross-host transport replaces the stub.
- **VL-061 (reference enforcing target; finish line A for step 4):** `IMPLEMENTATION/reference_target.py` is the deployable reference target (`uvicorn IMPLEMENTATION.reference_target:app`) promoted out of scaffolding  -  the "single largest not-built item for (A)" (artifact 12 section 3). It fetches and anchor-verifies the published record via the production `published_source.fetch_published_record`, then calls `verify_envelope(..., record_source=<fetched>, pinned_public_keys=<pinned gate key>)`, acting (200, recorded once) iff verify accepts and 403 otherwise. Critically, its accept criterion is solely "verify accepts against the anchor-verified fetched record AND the pinned gate signature verifies"  -  NOT calibrated to any author happy-path vector (the finish-line-(B) requirement: a target an external attacker can point at must not be tuned to the author's vectors). Exercised over the CURRENT loopback transport. Evidence `EVIDENCE/proofs/g5_reference_target_001_runner.py` (7 cases + acted-exactly-once, env-configured, real http.server fetch). G5 NOT closed: the gate->target hop is still modeled at this step; real cross-host TLS is steps 2-3 (VL-063); (B) needs an external attacker.
- **VL-063 (multi-process + real-TLS chain; steps 2-3 at single-host fidelity):** `IMPLEMENTATION/publisher.py` (NEW) promotes the runners' ephemeral http.server into a deployable published-record service serving `EVIDENCE/published_hashes.json` verbatim (trust still placed only in the target's anchor-verify, not the publisher/transport); `reference_target.py` gains a read-only `GET /received` count (observability, not a trust surface). `EVIDENCE/proofs/g5_multiprocess_tls_001_runner.py` generates a local test CA + leaf cert and runs publisher / reference target / gate as three separate OS processes over HTTPS, exercising four real TLS hops; honor is driven THROUGH the gate (gate->target->publisher) and confirmed via `/received` (no capture/redeliver), forge / replay / target_url-swap / absent-envelope posted directly to the target. ALL INVARIANTS HOLD, exit 0. **This is finish line (A) at single-host fidelity (real TLS between distinct OS processes on one box); it is NOT (B):** no second machine, no external attacker. The docker-compose file, the two-real-VM promotion with real-CA certs, and a public surface remain deploy-target artifacts; G5 CLOSED requires an external attacker on a real surface (GR-3).

**A3b  -  continuity / freshness sub-cases (VL-065, VL-066; the temporal half of replay-resistance).** A3 same-state replay (binding) was closed under G4 at VL-037/VL-038; A3b is the finer continuity family the cross-host wedge surfaced (`T-G5-continuity`):
- **Sub-case (a)  -  decision freshness: CLOSED (VL-065).** `reassert()` has no temporal dimension, so a captured, validly-signed ELIGIBLE envelope was honored arbitrarily later as long as canon/evaluator/manifest were unchanged (pinned by a failing test). The fix: the default ELIGIBLE forward in `pep.py` now stamps a SIGNED `not_after` (`DECISION_MAX_AGE_SECONDS`, default 300) inside the signature (tamper-proof window) and in `_HASH_EXCLUDED_KEYS` (so `decision_sha256` is byte-identical); the verifier enforces it at step 1.5b (`current >= not_after -> REF_VERIFY_SIGNATURE_EXPIRED`). The stale-decision case flipped honored -> refused. No new canonical invariant; time is not a repo-state hash, so `reassert()`'s five rows are unchanged.
- **Replay within the window / exactly-once: CLOSED (VL-066).** A time-window bounds how LONG a captured decision is usable but cannot distinguish a first use from an in-window replay; that needs the executor to REMEMBER. `sign_envelope(..., decision_id=...)` adds a per-issuance signed `decision_id` (also `_HASH_EXCLUDED_KEYS`); `pep.py` stamps `uuid4().hex`; the reference target keeps a TTL-bounded seen-set (`app.state.seen`, pruned at `not_after`) and refuses an already-honored `decision_id` with `REF_VERIFY_REPLAY` (verify_envelope stays pure  -  anti-replay is the acting party's stateful concern). The falsifiable wedge claim now holds in-process end-to-end, demonstrated on an MCP-shaped tool-call surface (`EVIDENCE/proofs/wedge_agent_toolcall_001_runner.py`, 7/7, tool fired exactly once). **Update (VL-076, B3):** the shared-replay-cache SEAM is now BUILT - `IMPLEMENTATION/replay_cache.py` (`ReplayCache.check_and_claim`; an `InMemoryReplayCache` byte-identical to the inline seen-set, and an `ExternalStoreReplayCache` over an injected shared store for cross-instance exactly-once). It is consumed by the MCP server (VL-077) and the executor SDK (VL-078) in its in-memory form; the cross-instance shared cache is unwired on the default `reference_target.py` path (still the inline per-instance dict). readiness.json `shared_replay_cache`: built / unwired. The genuinely-hard distributed-dedup is the SHARED-store deployment, still the author's.
- **Sub-case (b)  -  record freshness: READER BUILT (VL-074, B1), DEFAULT-PATH WIRING OPEN.** The signed published-record reader `IMPLEMENTATION/published_record_source.py` (publisher signature + `not_after` + monotonic serial) refuses a stale record with `REF_VERIFY_PUBLISHED_RECORD_STALE` / `REF_VERIFY_PUBLISHED_RECORD_INVALID`. It is build-then-wire: the default consult path still uses the byte-anchor reader (`published_source.py`), so a stale-but-anchor-matching record is still honored on the DEFAULT path until the reader is wired (readiness.json `published_record_freshness`: built / unwired; parity VL-039 seam -> VL-060 wire). Cross-host clock-skew tolerance is now BUILT too (VL-075, B2: a configurable `clock_skew` window, default 0 / byte-identical, on every consume-side freshness check).

**Phase B/C build (VL-074..VL-083) - G5-preparedness, G5 still NOT CLOSED.** The artifact-13 road hardened the wedge and packaged the surface as far as in-house work allows; none of it closes G5 (which needs a real external attacker on a real surface, GR-3):
- B1 record-freshness reader (VL-074), B2 clock-skew window (VL-075), B3 replay-cache seam (VL-076) - capabilities built, default-off (readiness.json: built / unwired with named blockers).
- B4 real MCP server (VL-077, `mcp_server_001_runner.py`, real stdio subprocess) and B5 executor SDK + latency harness (VL-078) - the wedge property on a real MCP surface + a thin integration; latency indicative (sandbox).
- C1 deploy packaging (VL-081) and C2 real-TLS tooling (VL-082) - Dockerfile / compose / cert tooling authored; the container/TLS STAND-UP is UNVALIDATED (no docker / real CA in-sandbox); the config bootstrap + cert material ARE validated (round-trip admit->verify; a real in-memory TLS handshake).
- C3 attack harness + falsifiable claim sheet (VL-079, `attack_harness.py` / `attack_suite_001_runner.py` / `docs/methodology/falsifiable_claim_sheet.md`) - the gate-2 attacks runnable and defeated IN-PROCESS; the HttpSurface adapter is ready for the real surface.
- C3-live runner (VL-083, `attack_suite_live_runner.py`, AUTHOR-executed, CI-excluded) + C4 `REAL_TRANSPORT` readiness predicate (RED, VL-083) - staged for the author's real-transport run.
**G5 status: NOT CLOSED.** Every in-house-authorable item is done; G5 CLOSED requires the author to stand up C1/C2 on real hosts, run the live attack suite green over real transport (flipping REAL_TRANSPORT green), and face a real EXTERNAL attacker (GR-3).

### G7  -  Tests are code-derived, not canon-derived
- **Code:** `test_pep.py` asserts the *implemented* behavior  -  version drift, SHA256 match,
  fail-closed forwarding. All four pass.
- **Canon:** Envelope domain: `TESTS/adversarial/test_ccs_canonical.py` (VL-028) derives nine tests
  from canon sections 11.9, 12.1, 12.3, 12.4, 13 with explicit citations in each docstring. Evaluator
  domain: `TESTS/adversarial/test_evaluator_canonical.py` (VL-034) derives 22 tests from canon sections
  11.7 (AC^3), 11.8 (T^26), and 11.9 (manifest-integrity, via artifact-05-layer per Decision C) with
  explicit citations in each docstring.
- **Delta:** Code-derived tests confirm the code; they cannot detect drift *from canon*  -
  this is precisely how G0 went unnoticed. Green tests certified "CCS" that does not match section 12.
- **Status: RESOLVED** (VL-028 + VL-029 + VL-034) - envelope domain closed via canon-derived
  tests at VL-028 (the post-VL-029 envelope.py and pep.py wiring exercise those tests on every
  ELIGIBLE response); evaluator domain closed via canon-derived tests at VL-034
  (`test_evaluator_canonical.py`, 22 tests; full suite 106/106 green). Both domains now have tests
  whose lineage runs from canon to assertion.
- **Action:**
  1. Add canon-derived tests for the envelope domain (section 12.1, 12.3, 12.4, 13).
     **DONE under VL-028** (`test_ccs_canonical.py`).
  2. Add canon-derived tests for the evaluator domain (section 11.7 AC^3, section 11.8 T^26,
     section 11.9 manifest-integrity). **DONE under VL-034** (`test_evaluator_canonical.py`).

### G8  -  Proof docs are narrated, not executable
- **Code:** The real evidence is the pytest suite.
- **Claimed:** `EVIDENCE/*.md` describe outcomes in prose.
- **Delta:** No proof is machine-checkable.
- **Action:** Each proof in `EVIDENCE/proofs/` names the test(s) backing it and the commit
  they passed at. Add CI; make `STATE.md` regenerable.
- **Status: NEAR-CLOSED** (VL-052, status note) - the machine-checkable half is met:
  `EVIDENCE/proofs/` carries executable runners (g3 enforcement, g4 refused-bypass, g5
  cross-host, g5 signed-cross-host, signing-forgery-defeated, root-recovery-cross-host,
  and siblings), each exiting 0, superseding the narrated prose proofs (VL-050 finding 4).
  Residual: no CI harness and `STATE.md` is not auto-regenerable. Not a RESOLVED flip;
  status recorded, no proof rewrite.
- **VL-073 (CI half closed):** the CI harness now exists. `.github/workflows/ci.yml`
  (GitHub Actions) runs the full pytest suite + every hermetic `EVIDENCE/proofs/` runner on
  push and pull_request and fails the build on any non-zero exit. Confirmed GREEN on GitHub
  Actions at commit `c519f34` (VL-073 build + follow-ups 1-3: the g4 signing-key repair, the
  multiprocess-runner hardening, a concurrent-test de-flake, and the documented exclusion of
  the two CI-incompatible runners - external webhook (non-hermetic) and multi-process-TLS
  (hosted-runner networking); the cross-host evidence class stays CI-gated by g5_cross_host /
  g5_signed_cross_host / root_recovery_cross_host). The Action's "Add CI" half is met; the
  residual narrows to the one remaining item, `STATE.md` auto-regenerability. Still
  NEAR-CLOSED, not RESOLVED.

### G9  -  `stability_proof_001.md` is truncated
- **Claimed:** Sets up a 50-iteration stability test, ends mid-JSON with no results.
- **Delta:** The one stability proof contains no proof.
- **Action:** Finish it or delete it.
- **Status: NEAR-CLOSED** (VL-052, status note) - `EVIDENCE/archive/stability_proof_001.md`
  carries a NON-CURRENT / ARCHIVED header citing G2 / G5 / G9 (archived 2026-05-15,
  ledger VL-011): the truncated proof was preserved-marked-non-current, the third path the
  Action did not enumerate (VL-050 finding 4). Status recorded; no archive-file edit.

---

### G11  -  Manifest-source asymmetry in SHA256 check  *(surfaced by VL-012)*
- **Code:** `evaluator.manifest_integrity_valid()` (formerly `ccs_valid()`)
  calls `manifest_sha256()` which reads `MANIFEST/manifest.json` from disk
  via a hardcoded path, ignoring the `manifest` argument passed to the
  function.
- **Delta:** Tests in `TESTS/test_concurrency.py` define inline manifests
  (`TEST_MANIFEST`, `MUTABLE_MANIFEST`) with different schemas from the
  on-disk file. The tests pass because their `expected_manifest_sha256`
  values happen to match the on-disk file, not the inline test fixtures.
  The check is internally inconsistent: AC^3 and T^26 verify against the
  passed manifest argument; SHA256 verifies against disk.
- **Action:** Resolved at VL-053 via path (b)-with-guard: the API contract
  is explicit that `manifest_sha256()` always hashes the on-disk
  `MANIFEST/manifest.json` (the single pinned source of truth), AND
  `manifest_integrity_valid()` fails closed when its passed `manifest`
  argument diverges from that on-disk source. Path (a) (hash the passed
  dict) was rejected at Checkpoint B: it changes the VALUE
  `manifest_sha256()` returns (file-bytes -> canonical-dict), which ripples
  into the envelope's `manifest_sha256` field, `decision_sha256`, artifact
  05's line-51 contract, and the literal manifest-SHA test pins. Path (b)
  leaves the `manifest_sha256` value unchanged, so those stay true. Both
  paths edit `evaluator.py` and therefore roll `evaluator_sha256` forward in
  the committed `EVIDENCE/published_hashes.json` -- the canon-12.4-expected
  consequence of any deliberate evaluator change, regenerated at VL-053 via
  `EVIDENCE/published_hashes_gen.py` (only that field moved; `canon_sha256`
  and `manifest_sha256` byte-identical). Path (b)'s smaller blast radius is
  the manifest-value invariance, not avoiding the committed record.
- **Status: RESOLVED** (VL-053). Build: the divergence guard in
  `IMPLEMENTATION/evaluator.py::manifest_integrity_valid()`. Test:
  `TESTS/adversarial/test_evaluator_canonical.py::test_manifest_integrity_rejects_divergent_manifest`
  (canon section 9 + 11.9; fails on the pre-VL-053 split-source True,
  passes on the guard's fail-closed False; sha derived live per constraint
  i). Masked-bug check: the divergent-manifest callers were in
  `TESTS/test_concurrency.py` (inline `TEST_MANIFEST`/`MUTABLE_MANIFEST`,
  Delta above), not on any production path (`pep.py` uses
  `load_manifest()`); repointed to the on-disk manifest at VL-053.
- **Prose tail cleared (VL-055):** the post-VL-053 stale `reassert()` Row-4
  comment in `IMPLEMENTATION/envelope.py` (it had described the asymmetry as a
  live flagged-open pattern) corrected to record this closure; the three
  literal manifest-SHA pins (VL-053 finding 5) in
  `TESTS/test_adversarial_evaluator.py`, `TESTS/test_pep.py`, and
  `TESTS/test_replay_receipts.py` converted to live `manifest_sha256()`
  (constraint-i / GR-1-safe). Behavior-inert; no status change (RESOLVED stands).
- **Related:** G6/G10 disambiguation pass (VL-012) surfaced this during
  full read of `test_concurrency.py`; not in pass scope.

---

### G12  -  Canon section 11.1 under-specifies wire-origins of `I`'s components  *(surfaced by VL-015)*
- **Canon:** Section 11.1 defines the interaction tuple `I = (A, S, C, t)`
  but does not specify whether `C` (context) or `t` (time) are
  caller-supplied on the wire or system-derived. Section 11.9 explicitly
  specifies that `AR(I)` and `R(I)` are "derived exclusively from M";
  no comparable wire-origin clause exists for `C` or `t`. The silence
  is *meaningful* (not merely absent) because canon elsewhere
  demonstrates capacity to specify wire-origin when it intends to.
- **Code:** `pep.py` accepts `context: Dict[str, Any]` opaquely; no time
  field is on the wire. The interpretive choice (C caller-supplied, t
  PEP-supplied) was made silently in the schema's pre-VL-016 draft.
- **Delta:** Three procedurally-clean derivations (Claude, Grok, OpenAI)
  diverged on `C` and `t` specifically, and only on those components.
  The divergence traces to canon under-specification, not to verifier
  error. VL-016 premise verification confirmed the under-specification
  unanimously (premise 1 classified Under-specified by both Grok and
  OpenAI). OpenAI's argument-from-contrast framing is incorporated.
- **Status: PARTIALLY ADDRESSED** - schema-layer half closed (VL-016);
  canon-layer half open.
- **Action:**
  1. Make the interpretive choices for `C` and `t` explicit in the
     schema with rationale. **DONE under VL-016** (decision 1A:
     context stays caller-supplied required with section-12.1 reasoning;
     decision 2B: t stays NOT caller-supplied with section-9 +
     section-12.4 fail-closed reasoning).
  2. Resolve the canon-layer under-specification via a canon-version
     event under GR-1 (e.g., v0.9.8.5 or v0.10 adding wire-origin
     clauses for `A`, `S`, `C`, `t` analogous to section 11.9's
     clause for `AR`/`R`). **OPEN** - not currently scheduled;
     canon-version events are out of band per GR-1.

### G13  -  Manifest-pinning field provenance is mixed canon + envelope  *(surfaced by VL-015)*
- **Canon:** Section 11.9 requires the manifest to be "deterministic,
  versioned, and integrity-verifiable" as a property of the manifest
  itself. Section 12.4 lists manifest version change as an invalid
  transition. Neither clause specifies that the *request* must carry
  caller-asserted version/hash fields.
- **Code:** `manifest_integrity_valid()` (VL-012) consumes
  `expected_manifest_version` and `expected_manifest_sha256` as
  caller-asserted fields and refuses on mismatch. The fields are
  load-bearing per VL-012's convention.
- **Delta:** The schema's pre-VL-016 attribution ("canon basis:
  section 11.9 + section 12.4") implied pure-canon derivation. The
  wire mechanism (caller assertion of expected version + expected hash)
  is in fact an envelope-spec operationalization (Deliverable 05) that
  realizes section 11.9's required manifest properties on the wire,
  not a direct canon-clause requirement. VL-016 premise verification
  confirmed this unanimously (premise 2 classified Supported: canon
  requires manifest properties but does not require wire-level
  caller-asserted fields; premise 3 classified Supported: the
  envelope-spec operationalization is consistent with what canon does
  and does not say).
- **Status: PARTIALLY ADDRESSED** - schema-layer half closed (VL-016);
  canon-layer half open.
- **Action:**
  1. Correct schema attribution for `expected_manifest_version` and
     `expected_manifest_sha256` to make the layered provenance
     explicit (canon required properties + envelope spec
     operationalization). **DONE under VL-016** (decision 3B: both
     the canon mapping table rows and the field-by-field sections
     updated; PROVENANCE NOTE added to the section-11.9 mapping
     section).
  2. Either (a) promote the envelope spec to a status that makes
     the layered provenance explicit in canon's framing, or
     (b) amend canon section 11.9 to explicitly authorize wire-
     level caller assertion of manifest properties. Both routes
     require canon-version event under GR-1. **OPEN** - not
     currently scheduled.

- **G14** - unknown-key refusal code under-determination inside `interaction`. **RESOLVED** (VL-054, Option A): an unknown non-CCS-shaped key directly inside `interaction` is refused with the cause-naming code `REF_SCHEMA_UNKNOWN_KEY`, replacing the provisional `REF_SCHEMA_TYPE_MISMATCH` mapping VL-018 used as the closest extant code (TYPE_MISMATCH's natural reading is "field type is wrong," not "field is unexpected"). Two surface events had corroborated the gap: VL-017 (test author's module docstring at `TESTS/adversarial/test_request_schema.py` lines 31-37) and VL-017b (OpenAI's Candidate 2 from the dry-run build-resumption test). Spec commit `a2c5d41` added the "Unknown key inside `interaction`" entry to `SPEC/request_schema.md` "Rejected shapes" naming the new code; build commit `5df3918` flipped `IMPLEMENTATION/request_validator.py` step 4d to emit it (the single emission point - the step-5 `REF_SCHEMA_TYPE_MISMATCH` returns and the `REF_SCHEMA_PARSE_ERROR` boundary are byte-unchanged) and added the spec-derived reject case `unknown_key_inside_interaction` (schema 27 -> 28, repo 202 -> 203). Lower-severity than G11: there was no silent-wrong-answer (the key was always refused; only the reason code was imprecise).
---

## Resolved gaps

### G6 / G10 / G0-rename - disambiguation pass complete
- **Closed:** 2026-05-15 (VL-012).
- **Convention adopted:** caller-asserted fields are REMOVED if redundant
  with system-verified checks; KEPT and DOCUMENTED if load-bearing.
  Asymmetric-by-function, by design.
- **G6 outcome:** `ctx["ccs_valid"]` removed from `ccs_valid()` (renamed to
  `manifest_integrity_valid()`). The field was redundant with the
  SHA256 + version match.
- **G10 outcome:** `ctx["expected_manifest_version"]` and
  `ctx["expected_manifest_sha256"]` retained; caller-assertion semantics
  documented in the `manifest_integrity_valid()` docstring. The G10
  finding extended in scope to cover both pinning fields once full read
  of `evaluator.py` surfaced the SHA256 field as the same pattern.
- **G0-rename outcome:** function renamed; name "CCS" reserved in code
  and in test IDs. G0's substantive (canonical CCS build) portion
  remains open as the G0 build track.
- **Test surface:** four `ccs_flag_*` cases deleted; four `ccs_version_*`
  cases renamed to `manifest_version_*`; one new `manifest_sha256_missing`
  case added to preserve coverage of the SHA-missing REFUSE path.
  Net suite size: 37 -> 34.
- **Related new gap G11:** the manifest-source asymmetry in
  `evaluator.manifest_sha256()` (reads from disk, not from the manifest
  argument) was surfaced by this pass and is recorded as G11 in the
  Open gaps section.

---

## Priority order

1. **G0**  -  the anchor. **RESOLVED** (VL-012 rename half + VL-029 build half). The substantive finding is now closed.
2. **G7**  -  without canon-derived tests, the next G0 is invisible. **RESOLVED** (VL-028 closed envelope domain; VL-034 closed evaluator domain).
3. **G0 rename + G6 + G10**  -  RESOLVED (VL-012). See Resolved gaps.
4. **G2**  -  request schema drift. **RESOLVED** (VL-014 + VL-015 + VL-016 schema track + VL-017 failing tests + VL-018 validator + VL-019 PEP wiring; `SPEC/request_schema.md` is the single source of truth, `IMPLEMENTATION/request_validator.py` wired into `pep.py`). **G12 + G13** (canon-layer halves)  -  OPEN, pending a canon-version event under GR-1.
5. **G3**  -  reframe public materials once 06 makes the FULL/PARTIAL/DRIFTED picture concrete. **RESOLVED at VL-030** (README rewrite + Zenodo Revision 2).
6. **G1**  -  RESOLVED (VL-052; README count-discipline on disk). **G8, G9**  -  NEAR-CLOSED (VL-052 status notes: executable runners supersede narration; the stability proof is archived non-current). **G11**  -  bookkeeping; owes its own spec-then-build increment. (G11 added VL-012; G2 removed from bookkeeping by VL-016 since it now has its own active track at item 4.)
7. **G4, G5**  -  build-outward scope, after the base is honest.
