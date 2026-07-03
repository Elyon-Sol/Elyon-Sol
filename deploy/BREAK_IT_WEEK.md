# Break-It Week — a time-boxed event to manufacture urgency

An open-ended challenge has no deadline, so nobody blocks time for it. A named window creates
urgency, concentrates attempts (a cluster is more likely to surface something than a trickle),
and produces social proof. Run it once the pre-launch gates are green.

Fill before announcing: [DATES] (a 7-day window), [SITE URL].

## Pre-flight (all must be true before you announce)

- [ ] Live self-test green over the public surface, run inside the week (attack suite exit 0).
- [ ] Cert-renewal hooks confirmed on all four nodes (no mid-window expiry — certs valid to
      2026-09-14, so any window before then is safe).
- [ ] Authorization-to-Test on file; safe-harbor wording final.
- [ ] `BREAK_IT_IN_60_SECONDS.md`, `INSPECT_YOUR_BREAK.md`, and `WALL_OF_FAME.md` published.
- [ ] Intake ready: security@elyon-sol.io monitored daily during the window.

## The week

- **T-7 days:** announce (copy below) across LinkedIn, Show HN, r/netsec, the target list,
  and every warm intro. Pin the quickstart and the wall of fame.
- **During:** answer only operational questions (is it up, what's the wire shape). Do NOT
  explain the design, defend a refusal, or hint at intended attacks — the claim sheet is the
  only guidance (per artifact 29, §4.4). Reproduce each submission within 24h; update the
  wall of fame live as findings land.
- **T-0 close:** post the outcome honestly either way — a confirmed break with the finder
  named, or "N attempts, no confirmed break within this scope and window" (never
  "unbreakable"). Ledger the run as a VL entry: it is the first real external-attempt referent
  whichever way it goes.

## What a clean week actually buys you

Even zero breaks is a result worth having: a scope-and-window-bounded record of external
attempts that found nothing is the honest, citable "external attempt" your project has never
had. It does NOT prove the system unbreakable — say so — but it moves G5 from "no external
party has ever tried" to "an external cohort tried under these terms." That is the first real
step across the door.

---

## Announcement copy (paste-ready)

> **Break-It Week: [DATES]. A live admission gate. First blood wins.**
>
> For one week we're daring the security community to break Elyon-Sol — a fail-closed
> admission gate where every approved action carries a one-time, Ed25519-signed token bound
> to exactly that action and target. The claim: without the signing key, you cannot make the
> target act unless the token is validly signed, current, correctly bound, and unused.
>
> It's live over real TLS, and you can throw your first attacks in ~60 seconds — no signup:
> [SITE URL]/#redteam. A tool tells you if your break is real. First person to make it act on
> a call it should refuse takes permanent first-blood on the public wall of fame — plus a
> named ledger entry, a CVE where it applies, Zenodo co-credit (your ORCID), and an invite to
> author the fix. No cash — durable credit.
>
> Honest scope: nobody outside the project has tested this yet. This week is how we find out.
> Come break it. security@elyon-sol.io
