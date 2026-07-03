# Authorization to Test — Elyon-Sol Admission Gate (private engagement)

> Template. Fill the bracketed fields, have counsel review alongside `SAFE_HARBOR_CLAUSE.md`,
> then sign before any traffic reaches the hosts. For the private invite-only engagement
> (`PRIVATE_INVITE_PROGRAM.md`), this signed document evidences the authorization.

**Asset owner / authorizing party:** Justin Laporte ("the Owner")
**Contact:** admin@elyon-sol.io / justin@elyon-sol.io
**Program:** Elyon-Sol Admission Gate — Private Time-Boxed Test
**Engagement window:** [START date/time, TZ] → [END date/time, TZ]
**Platform / channel:** private invite-only engagement, run directly by the team
(entry via security@elyon-sol.io; see `PRIVATE_INVITE_PROGRAM.md`)

## 1. Authorized systems (IN SCOPE — and ONLY these)
- https://gate.elyon-sol.io:8443  (admission gate; POST /governed-call)
- https://target.elyon-sol.io:9443 (enforcing target; POST /target, GET /received)
- https://authz.elyon-sol.io:9243  (ext-authz sidecar; POST /authz)
- https://pub.elyon-sol.io:9143/published_hashes.json (signed published record)

## 2. Authorized activity
The Owner authorizes the named researcher(s) admitted to the private program to conduct
good-faith security testing of the systems in §1 during the engagement window, including
sending crafted requests intended to cause the target to ACT, the gate to ADMIT, or the
sidecar to ALLOW on a call the program claim sheet says must be refused, and to report
findings through the program with reproduction steps.

## 3. Out of scope (NOT authorized)
All systems and domains not listed in §1; the cloud provider, domain registrar, and
certificate authority; denial-of-service or availability attacks; social engineering of any
person; physical access; testing outside the engagement window; and any access to, alteration,
or exfiltration of data beyond what is necessary to demonstrate a finding. Pivoting from an
in-scope host to any other system is not authorized.

## 4. Rules of engagement
- Stay within §1 and the window. Stop and report if you access anything unexpected.
- No DoS, no social engineering, no physical, no out-of-scope systems.
- Use the assigned program User-Agent string on all test traffic.
- Coordinated disclosure: do not publish findings before the agreed disclosure date
  ([90 days] from triage), per the program policy.

## 5. Safe harbor
Good-faith research conducted within §1, §2, and §4 is authorized and the Owner will not pursue
legal action for such activity. Full clause: `SAFE_HARBOR_CLAUSE.md` (counsel-approved version
governs). Authorization may be revoked in writing; testing must stop on revocation.

## 6. No warranty / assumption
Testing is against live infrastructure provided as-is. Researchers act on their own
responsibility within the authorized scope; the Owner provides no warranty.

## Signatures
Owner: ______________________________  Date: __________  (Justin Laporte)

Researcher / platform acknowledgment: ______________________________  Date: __________
(The researcher's counter-signature, or written acceptance of the program terms by email, records this.)
