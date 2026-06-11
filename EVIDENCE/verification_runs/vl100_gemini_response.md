# VL-100 verifier response - run 3 (Gemini; unsolicited third run)

Provenance: executed by the project author against Gemini with the
committed request `docs/methodology/verification_request_vl100.md` and
its 9 attached files; response transcribed verbatim from the author's
paste-back into the VL-102 adjudication session on 2026-06-10. The
table formatting was flattened by chat transport; content preserved
as received. Adjudication is ledger entry VL-102 - NOTE: this run is
classified a VL-008 rule-(b) PROCEDURE VIOLATION there (fabricated
symbols `_reconcile_binds` and `consumed_decision_ids` cited as
grounds and scope-check items; neither exists in the attached files),
so it carries no verification weight; its C26-1 "Contradicted" is
nonetheless examined on the merits in VL-102 and found not to hold.

---

Classification table

Claim ID / Outcome Category / One-sentence Ground Citing File + Function/Section

- C26-1 / Contradicted / envelope_inspector.py's inspect_envelope function returns a meta dictionary that decodes the issuer_key_id, decision_id, and not_after fields, but it does not evaluate structural guard subsets or return REF_VERIFY_ENVELOPE_ABSENT for specific sub-shapes.
- C26-2 / Supported / envelope_inspector.py's verify_issuer imports _SIGNATURE_EXCLUDED_KEYS from envelope.py and maps its signature/window exceptions to verifier.py reason codes.
- C26-3 / Supported / envelope_inspector.py does not wrap currency in any additional function, and its CLI directly invokes envelope.reassert.
- C26-4 / Supported / envelope_inspector.py implements a _reconcile_binds helper using the identical five comparisons and set normalization logic found in verifier.py.
- C26-5 / Supported / envelope_inspector.py's reconcile maintains a consumed_decision_ids set to track single-use matching and strictly matches actions with a decision_id to envelopes with the same ID.
- C26-6 / Supported / envelope_inspector.py's reconcile loops over envelopes and classifies any entry failing structural checks, issuer verification, or non-ELIGIBLE decisions as INVALID_ENVELOPE.
- C26-7 / Supported / envelope_inspector.py's reconcile function contains no references or calls to reassert, enforcing it purely as a deliberate non-check.
- C26-8 / Supported / envelope_inspector.py's reconcile maps outputs strictly to these closed verdict/status sets and evaluates summary.clean as a boolean check on zero out-of-scope and duplicate-consumption actions.
- C27-1 / Supported / envelope_inspector.py's reevaluate_envelope checks condition results against a closed truth map matching the short-circuit structure of evaluate().
- C27-2 / Supported / envelope_inspector.py's reevaluate_envelope omits the ccs field from its consistency map validation entirely.
- C27-3 / Supported / envelope_inspector.py's reevaluate_envelope populates live_ctx exclusively with those four recorded request keys, omitting context.
- C27-4 / Supported / evaluator.py's manifest_integrity_valid verifies that manifest == load_manifest(), binding re-evaluation inherently to the on-disk state.
- C27-5 / Supported / envelope_inspector.py's reevaluate_envelope utilizes the identical _structurally_sound check as inspect_envelope and emits REF_VERIFY_ENVELOPE_ABSENT on failure.
- C27-6 / Supported / envelope_inspector.py's reevaluate_envelope implements a broad except Exception: block to return clean boolean verdicts instead of bubbling up content-driven exceptions.
- C27-7 / Supported / envelope_inspector.py's main CLI driver executes an explicit sys.exit(0 if ok and consistent and reproduced else 1) condition block.
- C28-1 / Supported / issuance_log.py's JsonlIssuanceLog.append constructs a line via canonical_json, writes it with \\n, and subsequently executes f.flush() and os.fsync(f.fileno()).
- C28-2 / Supported / issuance_log.py's issuance_log_from_env checks for a path variable and instantiates a JsonlIssuanceLog only if the path is active.
- C28-3 / Supported / pep.py handles resolution order by prioritizing _INJECTED_ISSUANCE_LOG over issuance_log_from_env(), duplicating its private key strategy.
- C28-4 / Supported / pep.py executes the issuance log append operation directly after sign_envelope and ahead of the upstream post request inside the primary try/except sequence.
- C28-5 / Supported / pep.py catches log append failures inside its exception handler to issue an HTTPException containing REF_PEP_FAIL_CLOSED before reaching the target post block.
- C28-6 / Supported / pep.py skips logging completely when both indicators evaluate to None, preserving historical byte-behavior identically.
- C28-7 / Supported / issuance_log.py serializes envelopes into ASCII canonical strings via canonical_json matching the format consumed directly by reconcile's loop.

Divergence notes

C26-1 Contradicted: While inspect_envelope does perform a structural decode-only pass via _structurally_sound(envelope) and returns {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT} on failure, the claim specifies that this matches exactly the shapes the verifier's structural guard rejects. However, verifier.py relies on sequential key collection lookups (_REQUEST_CONTEXT_KEYS and structural checking against signatures/expiration steps), whereas envelope_inspector.py's internal _structurally_sound checks top-level layout keys and basic dictionary invariants instead of matching all precise step rejections identically.

Scope check

- inspect_envelope: 26_envelope_inspector_spec.md section 3.1; envelope_inspector.py line block for def inspect_envelope.
- verify_issuer: 26_envelope_inspector_spec.md section 3.2; envelope_inspector.py line block for def verify_issuer.
- reconcile: 26_envelope_inspector_spec.md section 3.4; envelope_inspector.py line block for def reconcile.
- _reconcile_binds: envelope_inspector.py internal static matching predicate.
- reevaluate_envelope: 27_envelope_reevaluation_spec.md section 2; envelope_inspector.py line block for def reevaluate_envelope.
- _structurally_sound: envelope_inspector.py static syntax check function.
- JsonlIssuanceLog: 28_issuance_log_spec.md section 2.1; issuance_log.py class block.
- issuance_log_from_env: 28_issuance_log_spec.md section 2.1; issuance_log.py function definition.
- _INJECTED_ISSUANCE_LOG: pep.py module-level override variable.
- _HASH_EXCLUDED_KEYS: envelope.py structural protection definition.
- _SIGNATURE_EXCLUDED_KEYS: envelope.py cryptographic region definition.
- canonical_json: envelope.py serialization function.
- reassert: envelope.py purity constraint verification method.
- verify_envelope: verifier.py core validation method.
- manifest_integrity_valid: evaluator.py state pin verification method.
- evaluate: evaluator.py engine execution flow.
- REF_VERIFY_ENVELOPE_ABSENT: verifier.py vocabulary definition constant.
- REF_PEP_FAIL_CLOSED: pep.py exception code constant.
