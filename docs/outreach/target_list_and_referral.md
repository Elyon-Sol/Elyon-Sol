# Targeted outreach — who to reach, and the referral cold-mail

One credible person forwarding this to their circle beats a thousand LinkedIn impressions.
The goal of every contact is two-fold: get *them* to try it, and get *the name of the one
person they'd point at it*. Referrals compound; broadcast doesn't.

Keep the funnel gated: link the public site + the 60-second quickstart; do NOT send the
briefing pack, internal reviews, or cross-model verdicts until someone is vetted and
authorized (see `SOLICITOR_INTAKE_CHEATSHEET.md`).

## Where the right people are (novelty-for-credit, not cash)

**Protocol / crypto / authz researchers** — the natural adversary for this target.
- IACR / crypto mailing lists; PL & formal-methods groups (lead with "it's formally specified").
- Researchers who publish on capability tokens, macaroons, biscuit, SPIFFE/SPIRE, JWT/OAuth
  replay, or ext-authz — find recent authors on those topics and cold-mail template R below.
- Applied-security firm alumni via warm intro (Trail of Bits / NCC / Include Security types).

**CTF crews & university security clubs** — motivated by the puzzle and the résumé line.
- CTFtime top-team contact addresses; DEF CON / BSides villages (AI Village especially).
- University security/hacking clubs — email the club officers; a novel live target is a
  ready-made meeting activity. Offer the wall-of-fame as the prize.

**AI-safety / AI-security niche** — genuine mission pull; frame as verifiable AI oversight.
- OWASP AI Exchange / OWASP LLM Top-10 working group; MLSecOps community.
- LessWrong / AI Alignment Forum; frontier-safety and model-eval circles.

**Broad reach — teasers that route to email, never open signup**
- Show HN / Lobste.rs / r/netsec (mod-permitting) / r/crypto post of the quickstart + DOI.
- Mastodon infosec, X/Twitter appsec — the one-line dare + the quickstart link.

## Build your list (aim for 15-20 named contacts)

Fill this in; work top-down. Prioritize people who (a) have no prior Elyon-Sol exposure and
(b) publish on the adjacent topics above.

| # | Name / handle | Why them (recent work) | Channel | Sent | Replied | Referral given |
|---|---------------|------------------------|---------|------|---------|----------------|
| 1 |               |                        |         |      |         |                |
| 2 |               |                        |         |      |         |                |
| … |               |                        |         |      |         |                |

## Template R — the referral cold-mail (individual)

> **Subject: 60-second challenge — break a live signed-capability admission gate**
>
> Hi [NAME] — your work on [their macaroon / replay / authz / capability-token thing]
> is why I'm writing. I built a fail-closed admission gate: every approved action carries
> a one-time, Ed25519-signed token bound to exactly that action and target, re-verified
> before anything happens. The claim I want disproved: without the signing key, you can't
> make the target act unless the token is validly signed, current, correctly bound, and
> unused.
>
> It's live over real TLS and you can throw the first attacks in about a minute — no signup:
> [SITE URL]/#redteam (quickstart in the repo). No cash bounty; the reward is durable credit
> — a permanent named ledger entry, Zenodo co-credit with your ORCID, a CVE where it applies,
> and an invite to author the fix. It's a public good (AGPL), not a product pitch.
>
> Two asks: (1) if it looks interesting, take a swing; (2) whether or not you do — **who is
> the one person you'd point at this?** A name is as useful to me as an attempt.
>
> One thing up front, for fairness: have you come across "Elyon-Sol" before? I'm looking for
> genuinely fresh eyes.
>
> Thanks — Justin · security@elyon-sol.io

## Template F — the forward (for someone vouching to their circle)

> Passing this along — [Justin] built a live, formally-specified admission gate and is
> daring people to break it. Novel target, real TLS, credited (recognition not cash),
> and you can try the first attacks in ~60 seconds without signing up: [SITE URL]/#redteam.
> Worth a look if you like capability-token / replay / authz puzzles.
