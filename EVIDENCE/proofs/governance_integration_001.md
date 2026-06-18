# Governance integration proof 001 (design 3.3)

**Claim.** Feature 1 (human oversight) and Feature 2 (non-bypassable) COMPOSE: the only path to
executing a high-impact action is *through the gate* (mTLS) AND *with a valid human grant*.

**Runner.** `EVIDENCE/proofs/governance_integration_001_runner.py` (hermetic: a private dev CA +
the real `pep` ASGI app via TestClient with gate/approver keys injected in-process). Also pinned
as a suite test: `TESTS/test_governance_integration.py`.

**Four legs, all must hold (exit 0):**

- **A. direct bypass -> refused at TLS.** A connection to the target without the gate client cert
  fails the mTLS handshake (Feature 2). The target is never reached.
- **B. routed but unapproved -> 202, no execution.** A high-impact `ELIGIBLE` call with no grant
  returns `202 PENDING_APPROVAL`; `requests.post` is never called (Feature 1 hold, [FIX H6]).
- **C. routed + approved -> executes exactly once + reconciles clean.** A grant produced by the
  approver CLI releases the held decision; the target is called exactly once; the issuance +
  approval logs `reconcile_approvals` clean (no FORWARDED_WITHOUT_GRANT, [FIX H8]).
- **D. replayed grant -> refused, no second execution.** Re-presenting the same `grant_id` against
  a fresh 202 is refused; the target is not called a second time ([FIX H3] single-use).

**Run log:** `EVIDENCE/proofs/governance_integration_001.log` (RESULT: PASS).

**Honest scope.** This proves the two mechanisms compose in-process. The full non-bypassable
property is deployment-gated (Feature 2 layers 1 + 3 are operator-locus; see
`deploy/NONBYPASS_TOPOLOGY.md`), and the single-use / pending-set are single-instance until a
shared store is wired (R2). White-box; not external validation (GR-3).
