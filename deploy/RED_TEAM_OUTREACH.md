# Red-team outreach (paste-ready)

The engagement is PRIVATE and invite-only, run directly by the team - NO bug-bounty
platform (VL-125; re-affirmed VL-127: YesWeHack and platform listings are not engaged).
The solicitation channels are the public one-page site (which carries the standing
challenge, the recognition model, and the engagement disclaimer) and LinkedIn posts
(paste-ready drafts: docs/outreach/linkedin_redteam_posts.md). Every channel routes to
security@elyon-sol.io, then vetting + a signed Authorization-to-Test
(deploy/AUTHORIZATION_TO_TEST.md) before any traffic reaches the hosts.

## A. Short cold message (direct to an individual researcher)

Subject: Short invited engagement - break a live auth/admission API (claim sheet attached)

Hi [NAME] - I saw your work on [their JWT/OAuth/replay/crypto thing]. I've built a
deterministic, fail-closed admission gate for machine-initiated API calls: it issues a
signed "admissibility envelope" that a downstream target re-verifies (signature,
freshness, replay, binding, state-currency) before acting. I want someone with no prior
exposure to it to try to break it.

It's a live four-host surface over real TLS. There's a one-page claim sheet of specific
"the target must refuse X" challenges - you win by making the target act on something it
should refuse, with repro. Scope is the named hosts only; I'll send written
authorization-to-test and a reporting channel you control.

Time-boxed [~N hours] over [window]. There's no cash bounty - the rewards are durable
credit and ownership: a permanent named entry in the project's public verification
ledger, co-credit on the next Zenodo record (DOI + ORCID), a CVE where applicable, an
invitation to co-author the fix, and a founding red-team seat. Interested? One question
up front: have you come across "Elyon-Sol" before? (Looking specifically for a fresh
set of eyes.)

Thanks,
Justin

---

## B. Program brief (private, invite-only - no platform)

Program name: Elyon-Sol Admission Gate - Private Time-Boxed Test
Scope (in): https://gate.elyon-sol.io:8443, https://target.elyon-sol.io:9443,
  https://authz.elyon-sol.io:9243, https://pub.elyon-sol.io:9143/published_hashes.json
Scope (out): all other hosts; the cloud provider, registrar, and CA; DoS/availability;
  social engineering; physical.
Focus: a custom admission-control protocol. Researchers receive a claim sheet of
  refusal guarantees; a valid finding is causing the target to ACT (or the gate to
  ADMIT) on a call the claim sheet says must be refused, with reproduction.
Out-of-scope as findings (stated boundaries, not bugs): caller declining to route
  through the gate (A1), root/publisher key compromise, semantic legitimacy of an
  authorized action, denial of service.
Recognition (not cash): a confirmed break earns a permanent named entry in the public
  verification ledger, co-credit on the next Zenodo record (DOI + ORCID), a CVE where
  applicable, an invitation to co-author the fix, and a founding red-team seat; teams
  can earn a documented ownership/co-maintainer path. Window: [DATES TBD]. Disclosure:
  coordinated, 90 days.

---

## C. Vetting checklist before granting access

- [ ] Confirmed NO prior exposure to Elyon-Sol / the framework (gate-4 decontamination).
- [ ] Background is auth / protocol / crypto, not only web-app pentest.
- [ ] Signed Authorization_to_Test before any traffic hits the hosts.
- [ ] Reporting channel agreed (they control timing).
- [ ] Window + recognition terms agreed in writing.
- [ ] You have run the self-test green (attack_suite_live_runner exit 0) FIRST.

---

## D. Where to look

- LinkedIn (PRIMARY) - post the challenge from the author's profile; paste-ready drafts
  in docs/outreach/linkedin_redteam_posts.md. Route every reply to
  security@elyon-sol.io; access stays invite-only and vetted.
- The public one-page site (site/index.html) - carries the standing challenge, the
  recognition table, and the engagement disclaimer; every other channel links to it.
- GitHub + conference talks (DEF CON / BSides) - find people publishing on JWT/OAuth/
  macaroon/replay weaknesses; cold-message with template A.
- r/netsec, OWASP local chapters, security Discords - an interesting novel target
  ("come break my AI-agent admission gate") draws goodwill attempts.
- Upwork / Toptal - cold-brief individual security freelancers with template A; vet per
  C and paper per deploy/AUTHORIZATION_TO_TEST.md before any traffic.

NOT used: bug-bounty platforms (HackerOne / Bugcrowd / Intigriti / YesWeHack). The
platform path was retired at VL-125; authorization + vetting are handled directly by
the team via the signed Authorization-to-Test.
