# OpenAI - governance core cross-model review - 2026-06-18

Run against the XMODEL_REVIEW packet + the zipped source bundle at HEAD 6ea0ccd (post-VL-123).
Procedurally clean per VL-008: cited only in-scope path:line, gave the scope-confirmation line.
Verbatim (lightly reflowed):

[GL-01] static/injected approver trust can be gate-controlled - DEPLOYMENT-GATED, High, P3.
pep.py:122-132, approval.py:193-207, governance_wiring.py:80-87. Inject _INJECTED_APPROVER_KEYS =
{"not-gate-id": gate_public_key}, sign the grant with the gate private key under
approver_key_id="not-gate-id". verify_grant rejects only key_id == gate_key_id, then trusts whatever
public key map pep supplies; the startup guard checks "injected + non-empty," NOT signed-chain
provenance. Fix: pep resolve approver keys only through key_record_source + resolve_approver_keys, or
require the injected object to carry validated signed-chain provenance.

[GL-02] request-binding check is vacuous in pep - RULED OUT, Low, P2. pep.py:447-465,
approval.py:215-217, pending_store.py:116-125. pep passes expected_approval_request_id=grant_req_id,
so verify_grant compares the grant field to itself; the binding still holds via
_PENDING.check_and_consume.

[GL-03] audit guarantee is optional unless startup wiring runs - DEPLOYMENT-GATED, Medium, P6.
pep.py:245-254, pep.py:487-506, issuance_log.py:92-99, governance_wiring.py:92-96. The approval log
defaults None; the approved branch skips grant_consumed logging and still forwards; the startup guard
catches it only IF it runs. Fix: enforce approval-log presence in the REQUEST PATH when
requires_approval(...) is true, not only at startup.

[GL-04] undeclared multi-instance scale silently weakens single-use - DEPLOYMENT-GATED, High, P4.
replay_cache.py:193-214, pending_store.py:197-221, governance_wiring.py:32-38. Per-process in-memory
stores unless Redis configured or the flag declared. Fix: make topology explicit required config or
refuse high-impact mode unless shared stores present.

Properties not broken: P1 (no grant -> 202 before sign/forward; valid grant checked, pending-consumed,
replay-claimed, logged before forward), P5 (missing/malformed HIGH_IMPACT -> approval-required;
expired grants refuse). H1-H8 hold; H5 PARTIAL (resolver enforces signed role but pep still accepts
arbitrary injected maps); H8 holds only when approval log configured / startup guard enforced.
"I stayed within the provided sources and cited only them."
