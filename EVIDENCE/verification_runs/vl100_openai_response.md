# VL-100 verifier response - run 2 (OpenAI)

Provenance: executed by the project author against OpenAI with the
committed request `docs/methodology/verification_request_vl100.md` and
its 9 attached files; response transcribed verbatim from the author's
paste-back into the VL-102 adjudication session on 2026-06-10.
Verbatim below the line (table formatting flattened by chat transport;
content preserved); adjudication is ledger entry VL-102.

---

Classification table

Claim / Outcome / Ground

- C26-1 / Supported / inspect_envelope() performs structural decode only and returns {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT} when _structurally_sound() fails; _structurally_sound() is built from verifier structural-guard tuples.
- C26-2 / Supported / verify_issuer() imports _SIGNATURE_EXCLUDED_KEYS, verifies signature and not_after, and emits the same signature/window failure codes referenced by the spec.
- C26-3 / Supported / The module imports reassert; no wrapper is defined, and the CLI calls reassert() directly.
- C26-4 / Supported / _binding_holds() applies target URL equality, AP equality, OP equality, manifest-version equality, manifest-sha equality, and context canonical_json equality, matching verifier step-3 semantics.
- C26-5 / Supported / reconcile() consumes matched envelopes, tracks prior consumption, and requires decision_id equality whenever the action supplies a decision_id.
- C26-6 / Supported / reconcile() marks structurally unsound envelopes, non-ELIGIBLE envelopes, and issuer-verification failures as INVALID_ENVELOPE and excludes them from matching.
- C26-7 / Supported / No reconcile path calls reassert(); the module explicitly records currency as outside the matching predicate.
- C26-8 / Supported / Action verdicts are MATCHED, OUT_OF_SCOPE, DUPLICATE_CONSUMPTION; envelope states are CONSUMED, UNUSED, INVALID_ENVELOPE; clean is true iff out-of-scope and duplicate-consumption counts are both zero.
- C27-1 / Supported / _record_consistency() implements ELIGIBLE -> all true, REFUSE -> not all true, and treats malformed conditions or unknown decisions as inconsistent.
- C27-2 / Supported / _record_consistency() consults only ac3, t26, and manifest_integrity; ccs is ignored.
- C27-3 / Supported / reevaluate_envelope() rebuilds ctx from AP, OP, expected_manifest_version, and expected_manifest_sha256 only; context is not used. It runs evaluate() and the three condition functions separately.
- C27-4 / Supported / manifest_integrity_valid() returns False unless the supplied manifest equals load_manifest(), making live-state semantics inherent.
- C27-5 / Supported / Structural failure in reevaluate_envelope() returns {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT}.
- C27-6 / Supported / Content problems are converted into inconsistency classifications or conservative false conditions; the function judges rather than raising on content.
- C27-7 / Supported / CLI reevaluate returns success only when ok, consistent, and reproduced are all true.
- C28-1 / Supported / JsonlIssuanceLog.append() writes canonical_json(envelope) + "\n" in append mode and performs flush() plus fsync().
- C28-2 / Supported / issuance_log_from_env() returns a JsonlIssuanceLog when ELYON_ISSUANCE_LOG_PATH is truthy and None otherwise.
- C28-3 / Supported / _get_issuance_log() resolves injected log first and environment second, mirroring _get_signing_key().
- C28-4 / Supported / Logging occurs after sign_envelope(), before upstream forwarding, and inside the same envelope-construction fail-closed try/except.
- C28-5 / Supported / Append failures are caught by the enclosing fail-closed block and become REF_PEP_FAIL_CLOSED; forwarding occurs only after successful append.
- C28-6 / Supported / When no injected log and no environment path exist, _get_issuance_log() returns None and the ELIGIBLE path skips logging, preserving prior behavior.
- C28-7 / Supported / Logged entries are envelope JSON objects produced from the signed envelope and written as JSONL; reconcile() accepts issued-envelope dicts in that shape without transformation.

Divergence notes
None. All 22 claims are Supported by the attached implementation artifacts.

Scope check
The response uses only the following concepts and sources:
- inspect_envelope, verify_issuer, reconcile, MATCHED, OUT_OF_SCOPE, DUPLICATE_CONSUMPTION, CONSUMED, UNUSED, INVALID_ENVELOPE, summary.clean - Spec 26 sections 2-3.5 and envelope_inspector.py.
- _SIGNATURE_EXCLUDED_KEYS, reassert, signature region definition - envelope.py and Spec 26 sections 2/3.2.
- Verifier structural guard, binding comparisons, signature/window vocabulary - verifier.py and Spec 26 section 2.
- _record_consistency, reevaluate_envelope, evaluate, ac3_valid, t26_valid, manifest_integrity_valid, reproduced, consistent - Spec 27 sections 2-3, envelope_inspector.py, and evaluator.py.
- JsonlIssuanceLog, issuance_log_from_env, _get_issuance_log, issuance-log wiring, REF_PEP_FAIL_CLOSED behavior - Spec 28 section 2 and issuance_log.py / pep.py.
- Claim identifiers C26-1 through C28-7 and classification categories - verification request document.

Out-of-scope items used: None.
