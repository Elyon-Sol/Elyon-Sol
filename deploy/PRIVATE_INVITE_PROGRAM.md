# Elyon-Sol — Private Invite Program (setup pack)

Program-management copy for a PRIVATE, invitation-only red-team engagement run
directly by the team — no bug-bounty platform. Researcher-facing technical detail
lives in `RED_TEAM_BRIEFING.md` (the "Gargoyle" pack); the public one-pager is
`BREAK_IT.md` and the site at `site/index.html`. Interested researchers reach us
first at security@elyon-sol.io; qualified people and teams are invited individually.

> **HARD GATES before issuing any invitation (do not grant access until all are true):**
> 1. Publisher signing key that was exposed in chat is REGENERATED and re-pinned on the target.
> 2. Counsel has signed off on the SAFE HARBOR clause (below).
> 3. Live self-test green over the 4-node surface (attack_suite_live_runner, exit 0).
> 4. Cert-renewal hooks confirmed on ALL FOUR nodes.
> 5. Signed Authorization-to-Test on file for the named hosts and the named researcher.

---

## Program name
Elyon-Sol Admission Gate — Private Invite-Only Red-Team

## Program type / visibility
Private, invitation-only. No public platform, no open sign-up. Access is granted
directly by the team after a solicitation to security@elyon-sol.io and a passed
vetting check. Coordinated disclosure, 90 days. Engagements can be time-boxed per
researcher (a named window on the signed authorization) or run as a rolling invite.

## Summary (what this is)
Elyon-Sol is a deterministic, fail-closed admission gate for actions. You win by
causing the system to ACT / ADMIT / ALLOW on a call its claim sheet says must be
refused — with reproduction. This is a custom admission-control protocol, not a
typical web app; researchers receive a claim sheet of refusal guarantees and a token
inspector to check decisions themselves. Full interaction guide: the attached
briefing pack.

## Scope — IN
- `https://gate.elyon-sol.io:8443`  (admission point; POST /governed-call)
- `https://target.elyon-sol.io:9443` (enforcing target; POST /target, GET /received)
- `https://authz.elyon-sol.io:9243`  (ext-authz eligibility sidecar; POST /authz)
- `https://pub.elyon-sol.io:9143/published_hashes.json` (signed published record)

## Scope — OUT
All other hosts and subdomains; the cloud provider, domain registrar, and certificate
authority; denial-of-service / availability; social engineering; physical attacks;
automated scanner noise without a working exploit.

## What counts as a valid finding
Causing the **TARGET to ACT**, the **GATE to ADMIT**, or the **SIDECAR to ALLOW** on a
call that a defended claim-sheet row says must be refused — **with reproduction steps
and artifacts**. The defended rows (1–13) and the inspector are in the attached
briefing pack; a disputed "break" is settled by running the inspector on the submitted
artifacts.

## Out of scope AS FINDINGS (stated boundaries, not bugs)
- **A1** — a caller that simply does not route through the gate (calls the target directly).
  Closed by a target-side admission policy, not by the gate; out of what the gate claims.
- **ROOT** — compromise of the root/publisher signing key (out-of-band trust floor; true of
  any PKI-rooted system). Recovery is not claimed.
- **Semantic legitimacy** — "I described a harmful action in valid vocabulary and it passed"
  is by design; the gate guarantees an action is AUTHORIZED, not WISE.
- **Availability / DoS** — the gate trades availability for safety (fail-closed). Knocking it
  offline refuses everything; that is the design.

## Recognition and ownership (per unique, valid finding) — not a cash bounty
This is a recognition-based program. Elyon-Sol is an attempt to build a verifiable oversight
layer for AI actions — a public good — and we are recruiting researchers who want their name on
that work rather than paying per report. Every reward below is durable credit, real authorship,
and a documented stake in the project. All credit is attributed by name/handle or anonymous —
the researcher's choice, every time.

| Contribution | What the researcher receives |
|---|---|
| **Named break** (TARGET acts / GATE admits / SIDECAR allows on a must-refuse defended row, with repro) | Permanent named entry in the public verification ledger ("the &lt;researcher&gt; finding") · co-credit on the next Zenodo Enforcement-Evidence Addendum (DOI + ORCID; acknowledgment, or contributor/creator for a load-bearing break) · CVE where applicable · invitation to co-design the fix and be named its author · founding seat on the standing Elyon-Sol red team |
| **Guarantee weakener** (binding/freshness weakness; oracle/leak enabling a break; conditional bypass) | Ledger mention · repository and Zenodo acknowledgment · written reference · standing invitation to the next round |
| **Real issue, out of claim** (TLS/config, info disclosure, hardening) | Public credit in the security acknowledgments · listed as a project hardener · reference on request |
| **Defense-in-depth / info** | Named acknowledgment in the repository credits |

**For teams — creative ownership.** Teams that want to go beyond a single finding have a path to
real ownership: authorship of a named hardening module carried in the codebase and the Zenodo
record; a co-maintainer / advisory track on the governance layer with input to the roadmap and
design reviews; and, for substantial ongoing collaboration, a documented partnership arrangement
(including a stake in commercial-license outcomes of work the team authors, discussed case by
case). We would rather share credit and direction with people who helped earn it than pay a flat
rate for a report.

**Optional headline:** a named **"first valid break"** distinction — permanent, top-billed credit
in the ledger and the next Zenodo record — for the first reproduced break of ANY defended row.

## Submission requirements (a valid report must include)
1. The claim-sheet **row number** you broke.
2. **Reproduction steps** (exact requests, in order).
3. **Artifacts**: the request/response bodies and any tokens/envelopes involved, so the
   inspector can confirm the verdict.
4. Observed result (which of TARGET-acted / GATE-admitted / SIDECAR-allowed) and why the row
   says it should have been refused.

## Triage & SLA
- First response: within **3 business days**.
- Validation: maintainer reproduces and runs the inspector on the artifacts.
- Duplicates: first valid report wins; substantially similar later reports are duplicates.
- Disclosure: coordinated, **90 days** from triage, by mutual agreement.

## Vetting / decontamination (invite gate)
Invite researchers with an **auth / protocol / crypto** background (not web-app-only).
Confirm **no prior exposure** to Elyon-Sol or its framework before granting access
(gate-4 decontamination). Keep the internal repo, canon, ledger, and any cross-model
results OUT of the researcher's hands — they receive only the decontaminated pack.

## SAFE HARBOR (counsel must approve before any invitation)
Good-faith security research conducted within this program's scope and rules will not be
pursued legally; researchers acting in good faith and within scope are authorized to test the
named hosts for the authorized window. [Exact wording subject to counsel review — this is a
HARD GATE; do not invite anyone without sign-off.]

---

## Document inventory — what to attach / have on file
| Document | Status | Where |
|---|---|---|
| This program page (scope, rules, recognition, disclosure, safe harbor) | this file | `deploy/PRIVATE_INVITE_PROGRAM.md` |
| Public one-pager / challenge | HAVE | `deploy/BREAK_IT.md` · `site/index.html` |
| Researcher briefing pack (surface, claim sheet, inspector, reporting) | HAVE | `deploy/RED_TEAM_BRIEFING.md` |
| Solicitor intake cheat sheet (what to send, in order) | HAVE | `deploy/SOLICITOR_INTAKE_CHEATSHEET.md` |
| Authorization-to-Test (signed, named hosts + researcher) | HAVE (draft) — sign before access | `deploy/AUTHORIZATION_TO_TEST.md` |
| Safe-harbor clause (counsel-approved) | TODO — counsel sign-off (HARD GATE) | `deploy/SAFE_HARBOR_CLAUSE.md` |
| Live self-test green log | HAVE process | `deploy/LIVE_BRINGUP_RUNBOOK.md` / attack runner |
| Pre-launch checklist (key regen, cert renewal, self-test) | see HARD GATES above | `deploy/PHASE1_PRELAUNCH_RUNBOOK.md` |
