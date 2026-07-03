# Solicitor intake cheat sheet — what to give a red-team solicitor

Use this when someone emails **security@elyon-sol.io** asking to take part. The
engagement is private and invite-only: nobody touches the live hosts until they are
vetted and authorized. Give things out in order — never hand over the next item until
the current gate is passed. **The internal repo, canon, verification ledger, and any
cross-model results are NEVER shared** (that is the "gate-4 decontamination" rule; a
researcher who has seen them can no longer give a clean external result).

---

## The two buckets

**Public — fine to share with anyone, before any vetting**
- The one-pager / challenge: `site/index.html` (or the hosted URL) and `deploy/BREAK_IT.md`.
- The Zenodo record (canonical citation): https://doi.org/10.5281/zenodo.20751592
- The claim in one line: "Without the gate's signing key, you cannot make the target act,
  or the sidecar say ALLOW, unless the token is validly signed, current, correctly bound,
  and unused. Find where that's false."

**Gated — only after vetting + signed authorization**
- `deploy/RED_TEAM_BRIEFING.md` (the "Gargoyle" pack: full surface, claim-sheet rows 1–13,
  request/response shapes, the sample legitimate flow).
- The token/envelope **inspector CLI** + usage (so they can self-check a break before submitting).
- Live host details beyond the four public URLs, and the private reporting channel.

---

## Intake flow (do these in order)

1. **Acknowledge + qualify (email reply).** Thank them; ask for a one-paragraph background
   and any prior public work. Send the two PUBLIC items only. Ask the vetting questions (below).

2. **Vet.** Confirm:
   - Background is **auth / protocol / crypto**, not web-app-pentest only.
   - **No prior exposure** to Elyon-Sol, its canon, or its framework (decontamination).
   - Real identity or a verifiable handle/reputation; agrees to coordinated disclosure (90 days).
   - For a **team**: named members, who leads, and that all members pass the same check.

3. **Confirm the hard gates are met on our side** before authorizing anyone:
   publisher key rotated & re-pinned · counsel-signed safe-harbor clause · green live self-test
   over all four nodes · cert-renewal hooks on all four nodes · Authorization-to-Test ready.
   (Full list: `deploy/PRIVATE_INVITE_PROGRAM.md` and `deploy/PHASE1_PRELAUNCH_RUNBOOK.md`.)

4. **Authorize.** Send `deploy/AUTHORIZATION_TO_TEST.md` naming the researcher + the four hosts
   + the window; get it signed and on file. Send the counsel-approved safe-harbor clause
   (`deploy/SAFE_HARBOR_CLAUSE.md`). No traffic hits the hosts before this is signed.

5. **Grant access.** Now send the GATED bucket: `RED_TEAM_BRIEFING.md`, the inspector CLI +
   usage, the reporting channel, and the sample legitimate flow. Point them at the four scope
   hosts and the rules of engagement.

6. **Set expectations (the recognition model).** Restate what a valid finding is, how to submit
   (row number + repro steps + artifacts), the 3-business-day first response, and the
   recognition/ownership rewards (ledger credit, Zenodo co-credit, CVE, fix authorship, red-team
   seat; team ownership path). Rewards detail: `deploy/PRIVATE_INVITE_PROGRAM.md`.

7. **On submission.** Reproduce, run the inspector on their artifacts, classify, respond. A
   confirmed break becomes a named ledger entry + a fix or a documented limit, credited to them.
   A clean run is recorded as "not broken within this scope and window" — never "unbreakable."

---

## Quick reply template (paste + trim)

> Thanks for reaching out. Elyon-Sol is a private, invite-only red-team — we run it directly,
> not through a platform, and access is granted individually after a short vetting step.
>
> To start: (1) a paragraph on your background (we look for auth / protocol / crypto experience);
> (2) confirmation you've had no prior involvement with Elyon-Sol or its framework; (3) that
> you're OK with coordinated disclosure (90 days). Meanwhile, the public challenge and the claim
> you'd be trying to disprove are here: <one-pager URL> and https://doi.org/10.5281/zenodo.20751592.
>
> There's no cash bounty — the rewards are durable credit and ownership: a permanent named entry
> in our public verification ledger, co-credit on the next Zenodo record (with your ORCID), a CVE
> where applicable, an invitation to co-author the fix, and a founding seat on the red team; teams
> can earn a documented co-maintainer / ownership path. Once you're vetted and authorized we'll
> send the full briefing pack, the token inspector, and the reporting channel.

---

## Never send
- The source repository, `CANON/`, `EVIDENCE/verification_ledger.md`, or any cross-model transcript.
- Signing keys, host credentials, or anything that would let someone sign a token.
- Anything that reveals internal confidence, test results, or design rationale beyond the
  decontaminated pack.

---

## Where to find / recruit solicitors (curated, invite-only)

Because access is individual and vetted, favor **targeted outreach and credibility** over volume.
Post the public one-pager + Zenodo DOI and route everyone to security@elyon-sol.io.

**Best fit — protocol / crypto / auth researchers**
- Personal and academic networks: university security & formal-methods groups, IACR / crypto
  mailing lists, PL/formal-verification circles (the system is formally specified — lead with that).
- Applied-security firms' researchers via warm intros (Trail of Bits / NCC / Include Security-type
  backgrounds); curated infosec communities (e.g., The Many Hats Club, appsec Slacks/Discords).
- Conference villages & CTF crews: DEF CON AI Village, security CTF teams that like novel protocols.

**AI-governance / safety audience (mission-aligned)**
- MLSecOps community, OWASP AI Exchange / OWASP LLM Top-10 working group, AI red-teaming networks.
- LessWrong / AI Alignment Forum, and frontier-safety / model-eval communities — frame it as
  "help build a verifiable oversight layer for AI actions," not a bounty.
- Standards & policy circles: NIST AI RMF community, MLCommons, Partnership on AI.

**Broad reach — as a teaser that routes to email, not open sign-up**
- LinkedIn (PRIMARY channel, VL-127) — the challenge posted from the author's profile;
  paste-ready drafts in `docs/outreach/linkedin_redteam_posts.md`. Replies route to
  security@elyon-sol.io; no open sign-up.
- A "Show HN" / Hacker News post of the one-pager + the Zenodo record; Lobste.rs; r/netsec
  (mod-permitting) and r/crypto; Mastodon infosec and X/Twitter appsec.
- A short write-up on the project blog / Substack / Medium linking the challenge and the DOI,
  with a single call to action: email security@elyon-sol.io to be considered.

Lead every post with the same three things: the one-line claim to disprove, the recognition/
ownership model (not cash), and the intake address. Keep the funnel narrow and the vetting strict.
