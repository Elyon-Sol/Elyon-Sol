# Grok - governance core cross-model review - 2026-06-18

Run against the XMODEL_REVIEW packet + the zipped source bundle at HEAD 6ea0ccd (post-VL-123).
Procedurally clean per VL-008: cited only in-scope path:line, gave the scope-confirmation line.
Verbatim (lightly reflowed):

No exploitable breaks found in core properties on a correctly wired single-process deployment. All
[FIX H1]-[H8] hold in the implementation (not just docstrings), with strong negative results across
attempted attacks. The layer is tight, with explicit revert-catchers and fail-closed defaults.
Weakest paths are deployment-gated (operator misconfiguration or omitted shared stores).

No findings of P1-P6 violations on a correct single-process deployment. Attempts to construct breaks
(tampered grants, missing records, concurrent resubmits without shared stores, static pins, malformed
manifests) failed due to binding, SoD, atomic consume-before-forward, wiring guards, and audit
reconciliation.

Summary: P1 forward gate - holds (none on correct wiring, RULED OUT). P2 binding - holds (RULED OUT).
P3 SoD - holds; weakest path static pin (G-01), DEPLOYMENT-GATED. P4 single-use/scale - holds with
shared store; weakest path no shared store + multi-instance, DEPLOYMENT-GATED. P5 freshness/defaults -
holds (RULED OUT). P6 audit - holds; weakest path no approval_log configured, DEPLOYMENT-GATED.

P3 note: resolve_approver_keys excludes non-"approver" role; belt-and-braces key_id != gate_key_id;
wiring guard G-01/G-06; static pin is weaker but caught at startup for HIGH_IMPACT. P4 note: InMemory
catches in-process; shared Redis/Lua compare-and-delete atomic; no-shared + multi-instance degrades
but caught loudly by R-02 guards + wiring G-03. P6 note: reconcile_approvals detects
FORWARDED_WITHOUT_GRANT; wiring G-04 refuses startup on HIGH_IMPACT. H1-H8 all "Yes".
"I stayed within the provided sources and cited only them."
