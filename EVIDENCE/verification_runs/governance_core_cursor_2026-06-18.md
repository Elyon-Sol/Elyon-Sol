# Cursor (Mode-A white-box) - governance core review - 2026-06-18

Run against the repo at 6ea0ccd's predecessor (aa2dea0, pre-VL-123). White-box: full repo. Findings
drove VL-123. Verbatim (lightly reflowed):

Findings: G-01 static env approver pin bypasses R1 role-distinctness (POSTURE GAP, High, P3) -
pep.py _get_approver_keys static path + verify_grant SoD key_id-only; gate self-approve under a
different key_id. G-02 multi-worker without declare-or-fail or shared grant-replay store (POSTURE
GAP, High, P4). G-03 shared pending Redis without shared replay Redis (POSTURE GAP, High, P4) -
pending_store_from_env and replay_cache_from_env independent. G-04 P6 audit guarantee opt-in;
runtime forward does not require approval log (POSTURE GAP, Medium, P6). G-05 verify_grant request
binding in pep is a tautology (FALSE-ALARM, Low, P2 - load carried by check_and_consume). G-06 R1
bootstrap fails open to empty approver map (POSTURE GAP, Low, P3 - fail-closed at grant time, not
startup).

Bottom line: No Critical real bugs on a single-worker, R1+R2 fully wired surface. The
hold->verify->consume->claim->forward chain is correctly ordered and fail-closed. Exploitable gaps
are deployment posture (G-01 static pin; G-02/G-03 undeclared scale / partial Redis; G-04 optional
approval logging), all in-repo wiring preconditions documented in deploy/GOVERNANCE_DEPLOYMENT.md.
