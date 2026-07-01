# Red-team outreach (paste-ready)

## A. Short cold message (direct to an individual researcher)

Subject: Paid short engagement - break a live auth/admission API (claim sheet attached)

Hi [NAME] - I saw your work on [their JWT/OAuth/replay/crypto thing]. I've built a
deterministic, fail-closed admission gate for machine-initiated API calls: it issues a
signed "admissibility envelope" that a downstream target re-verifies (signature,
freshness, replay, binding, state-currency) before acting. I want someone with no prior
exposure to it to try to break it.

It's a live two-host surface over real TLS. There's a one-page claim sheet of specific
"the target must refuse X" challenges - you win by making the target act on something it
should refuse, with repro. Scope is two named hosts; I'll send written
authorization-to-test and a reporting channel you control.

Time-boxed [~N hours] over [window]. Compensation: [$X / negotiable]. Interested? One
question up front: have you come across "Elyon-Sol" before? (Looking specifically for a
fresh set of eyes.)

Thanks,
Justin

---

## B. Private bug-bounty program brief (HackerOne / Bugcrowd / Intigriti)

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
- [ ] Window + compensation agreed in writing.
- [ ] You have run the self-test green (attack_suite_live_runner exit 0) FIRST.

---

## D. Where to look
- HackerOne / Bugcrowd / Intigriti - run a PRIVATE, time-boxed program (handles
  authorization + vetting; researchers are genuinely blind). Best fit.
- GitHub + conference talks (DEF CON / BSides) - find people publishing on JWT/OAuth/
  macaroon/replay weaknesses; cold-message with template A.
- r/netsec, OWASP local chapters, security Discords - an interesting novel target
  ("come break my AI-agent admission gate") draws goodwill attempts.
- Upwork / Toptal - c