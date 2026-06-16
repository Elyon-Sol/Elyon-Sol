# Safe Harbor + Authorization to Test - DRAFT for counsel

> STATUS: DRAFT, uncommitted, NOT legal advice. This is a starting point for your
> attorney to finalize, based on the disclose.io standardized Safe Harbor template
> (disclose.io / disclose/policymaker, en-US). It is tailored to the Gargoyle "break
> it" program (BREAK_IT.md). Do NOT publish until counsel has reviewed and adapted it
> to your legal entity and jurisdiction. Once finalized, it replaces the
> `<Have counsel finalize this clause.>` placeholder in BREAK_IT.md section "Rules of
> engagement" and the standalone Authorization-to-Test referenced in
> RED_TEAM_BRIEFING.md.

---

## 1. Scope of authorization (the only systems you may test)

This authorization applies **only** to the following hosts, operated by
`<LEGAL ENTITY / OPERATOR NAME>` ("we", "us"):

- https://gate.elyon-sol.io:8443
- https://target.elyon-sol.io:9443
- https://authz.elyon-sol.io:9243
- https://pub.elyon-sol.io:9143

No other host, domain, subdomain, network, account, tenant, or service is in scope or
authorized. Testing anything not on this list is not covered by this authorization.

## 2. Safe Harbor

When you conduct security research in good faith according to this policy, we consider
that research to be:

- **Authorized** with respect to any applicable anti-hacking laws (for example, the U.S.
  Computer Fraud and Abuse Act and equivalent statutes), and we will not initiate or
  support legal action against you for accidental, good-faith violations of this policy;
- **Authorized** with respect to any relevant anti-circumvention laws, and we will not
  bring a claim against you for circumventing the technological measures that protect
  the in-scope systems (the gate signature, replay, binding, and freshness checks are
  the intended subject of your testing);
- **Exempt** from any restrictions in our Terms of Service or Acceptable Use Policy that
  would interfere with good-faith security research, which we waive on a limited basis
  for the in-scope systems above; and
- **Lawful, helpful to the overall security of the Internet, and conducted in good
  faith.**

You are expected to comply with all applicable laws at all times. If a third party
initiates legal action against you for activities you carried out in compliance with
this policy, we will take steps to make known that your actions were authorized and
conducted in compliance with this policy.

If at any point you are uncertain whether a specific action is consistent with this
policy, stop and ask us through the reporting channel below **before** proceeding.

> This Safe Harbor applies only to legal claims under our control. It does not bind
> independent third parties (for example, our cloud provider, domain registrar, or
> certificate authority), and it does not authorize testing of their systems.

## 3. Not authorized (out of scope, no safe harbor)

The following are **not** authorized and are **not** covered by this Safe Harbor:

- Denial-of-service, volumetric, load, or availability testing of any kind. The system
  is designed to refuse when uncertain; making it refuse or unavailable is not a finding.
- Social engineering, phishing, or any targeting of our staff, contractors, or any
  person.
- Attacks on, or access to, any system, account, tenant, or network not listed in
  section 1 - including the cloud provider, domain registrar, certificate authority,
  host operating systems, or other infrastructure obtained by means outside the
  request protocol.
- Physical access attempts.
- Accessing, modifying, destroying, or exfiltrating data that is not your own; degrading
  or disrupting service for others; or retaining any sensitive data you encounter (if you
  encounter any, stop and report it).

Reaching a stated by-design boundary (a caller that does not route through the gate; root
or publisher key compromise; the semantic-legitimacy question; denial of service) is a
documented limit, not a break - see BREAK_IT.md "What does NOT count."

## 4. Your obligations (good-faith conditions)

To stay within this authorization you must:

- Test only the systems in section 1, only during the stated engagement window.
- Make a good-faith effort to avoid privacy violations, data loss, and service
  disruption to us or to others.
- Use only your own accounts and test data; do not access another party's data.
- Report each suspected vulnerability promptly and privately through the channel in
  section 5, and give us a reasonable opportunity to remediate before any disclosure.
- Not publicly disclose any finding before the coordinated-disclosure window elapses or
  we agree otherwise in writing.

## 5. Reporting and coordinated disclosure

Report privately through `<OFFICIAL CHANNEL - e.g. the bug-bounty platform program, or
security@elyon-sol.io>`. Please allow **90 days** from your report for remediation
before any public disclosure; we will coordinate timing and credit with you. We aim to
acknowledge reports within `<N>` business days.

## 6. Engagement window and authorization period

This authorization is valid only from `<START DATE/TIME>` to `<END DATE/TIME>` (the
"engagement window") and only for the named researcher(s) granted access. Testing
outside that window or by anyone not granted access is not authorized.

---

## Counsel review checklist (delete before publishing)

- [ ] Insert the correct legal entity name and governing-law / jurisdiction clause.
- [ ] Confirm the anti-hacking / anti-circumvention non-pursuit language is enforceable
      in your jurisdiction(s) and for the researcher's likely jurisdiction.
- [ ] Confirm the CFAA reference (or local equivalent) is appropriately phrased.
- [ ] Decide whether to use the full disclose.io Safe Harbor (above) or the
      "Simple Safe Harbor" short form; confirm whether you can/should display the
      disclose.io logo / Core Terms (requires scope + official channel + disclosure
      policy per disclose.io).
- [ ] Confirm the data-handling clause matches your privacy obligations.
- [ ] Confirm the engagement-window mechanism (per-researcher, written grant) matches how
      you will actually run the program (a private bug-bounty listing handles much of this).
- [ ] Confirm reward/compensation terms are stated separately (BREAK_IT.md "Reward") and
      do not create unintended contractual obligations.
- [ ] Confirm the third-party (cloud / registrar / CA) carve-out is sufficient.

## Sources

- disclose.io Safe Harbor template (full): https://github.com/disclose/policymaker/blob/main/static/templates/disclose-io-safe-harbor/en-US.md
- disclose.io Simple Safe Harbor template: https://github.com/disclose/policymaker/blob/main/static/templates/disclose-io-simple-safe-harbor/en-US.md
- disclose.io project: https://disclose.io/
