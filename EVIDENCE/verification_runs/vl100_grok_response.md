# VL-100 verifier response - run 1 (Grok)

Provenance: executed by the project author against Grok with the
committed request `docs/methodology/verification_request_vl100.md` and
its 9 attached files; response transcribed verbatim from the author's
paste-back into the VL-102 adjudication session on 2026-06-10.
Verbatim below the line; adjudication is ledger entry VL-102.

---

Classification table

- C26-1: Supported. envelope_inspector.py:175 (inspect_envelope calls _structurally_sound which reproduces verifier's guard from verifier.py:290-298 using imported _REQUIRED_ENVELOPE_KEYS and _REQUEST_CONTEXT_KEYS; returns {"ok": False, "reason": REF_VERIFY_ENVELOPE_ABSENT} with no signature/currency/binding logic).
- C26-2: Supported. envelope_inspector.py:244 (imports _SIGNATURE_EXCLUDED_KEYS from envelope.py; builds signed region identically; performs signature verify + window check matching verifier.py:344-353 and 368-379 with identical REF_VERIFY_* codes).
- C26-3: Supported. No wrapper function around reassert in envelope_inspector.py (CLI at 595-598 calls it directly from imported envelope); verify_issuer and inspect_envelope explicitly omit it.
- C26-4: Supported. _binding_holds at envelope_inspector.py:393 (target_url), 396-398 (normalized AP/OP via imported _normalize_set_field from verifier.py:199), 402-405 (manifest pins), 409 (canonical_json context) matches verifier.py step 3 binding logic.
- C26-5: Supported. envelope_inspector.py:483 (decision_id match priority), 487-490 (consume on first match), 493-496 (set consumed flag preventing reuse).
- C26-6: Supported. envelope_inspector.py:454-465 (structural guard, decision=="ELIGIBLE", and verify_issuer when pinned_keys supplied mark INVALID_ENVELOPE and exclude from matchable).
- C26-7: Supported. No call to reassert anywhere in reconcile (envelope_inspector.py:478-507); docstring at 443 explicitly notes deliberate non-check.
- C26-8: Supported. envelope_inspector.py:497/500/503 (verdict set), 463/467/495 (status set), 515 (summary.clean exactly as defined).
- C27-1: Supported. _record_consistency at envelope_inspector.py:301-304 mirrors evaluator.py:123-130 short-circuit (ELIGIBLE requires all True; REFUSE requires not-all-True; malformed/unknown decision inconsistent).
- C27-2: Supported. _record_consistency at envelope_inspector.py:291-299 consults only _CONDITION_KEYS (ac3/t26/manifest_integrity); ccs ignored per comment at 288-290.
- C27-3: Supported. reevaluate_envelope at envelope_inspector.py:347-352 (ctx from exactly those four fields), 354 (evaluate), 361-363 (three conditions).
- C27-4: Supported. envelope_inspector.py:356-364 + evaluator.py:93 (manifest != load_manifest() fails integrity).
- C27-5: Supported. reevaluate_envelope:341-342 uses _structurally_sound returning REF_VERIFY_ENVELOPE_ABSENT shape matching inspect.
- C27-6: Supported. reevaluate_envelope always returns dict (no raises on content); judges via _record_consistency + live run.
- C27-7: Supported. envelope_inspector.py:602-603 (CLI exit 0 iff ok/consistent/reproduced).
- C28-1: Supported. issuance_log.py:53-57 (canonical_json + "\n", append mode, flush+fsync).
- C28-2: Supported. issuance_log.py:64-67 (env var check; None or JsonlIssuanceLog).
- C28-3: Supported. pep.py:137-141 (_get_issuance_log mirrors _get_signing_key injected-then-env).
- C28-4: Supported. pep.py:300-302 (after sign_envelope:289, before post_to_target:326, inside try:261-311).
- C28-5: Supported. pep.py:301-311 (append in try; exception -> REF_PEP_FAIL_CLOSED 403; no upstream call).
- C28-6: Supported. _get_issuance_log:138-140 + conditional if issuance_log is not None in pep.py:301 leaves ELIGIBLE path unchanged when default None.
- C28-7: Supported. issuance_log.py:53 (canonical_json envelope) + envelope_inspector.py:605/608 (JSONL load + reconcile accepts directly).

Divergence notes
None (all 22 claims Supported).

Scope check
All concepts/terms/claims (e.g. inspect_envelope, verify_issuer, reconcile, reevaluate_envelope, JsonlIssuanceLog.append, _binding_holds, _record_consistency, _get_issuance_log, REF_VERIFY_ENVELOPE_ABSENT, canonical_json, _SIGNATURE_EXCLUDED_KEYS, _normalize_set_field, structural guard, decision_id matching, pinned_public_keys, short-circuit logic, manifest_integrity_valid, etc.) derive from:

- 26_envelope_inspector_spec.md (sections 3.1-3.5, 2).
- 27_envelope_reevaluation_spec.md (sections 2.1-3).
- 28_issuance_log_spec.md (sections 2.1-2.2, 1, 3).
- envelope_inspector.py (functions, lines 145-616, imports).
- issuance_log.py (full).
- pep.py (lines 132-141, 293-311, _INJECTED_ISSUANCE_LOG etc.).
- verifier.py (guards, binding, REF_VERIFY_* at 169-189, 192-200).
- evaluator.py (evaluate/conditions at 117-136, 93).
- envelope.py (_SIGNATURE_EXCLUDED_KEYS). No out-of-scope items used.
