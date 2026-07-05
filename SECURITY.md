# Security Policy

Elyon-Sol is a deterministic, fail-closed admission gate. Its entire value is that it
refuses actions that are not authorized — so we take reports about the *core admissibility
claim* seriously and welcome adversarial testing.

## Reporting a vulnerability

Email **security@elyon-sol.io** with:

- the class of finding (target break / sidecar break / other),
- the exact requests in order (copy-pasteable), and
- what you observed (status codes, and — for a target break — the target's `/received` count).

We aim to acknowledge within a few business days, reproduce, classify, and respond. Please do
**not** open public GitHub issues for security findings.

## The core claim (what a "break" is)

Without the gate's signing key, there is no request you can craft that (a) makes the target
perform an action, or (b) makes the ext-authz sidecar answer `ALLOW`, unless the token in the
`X-Elyon-Sol-Envelope` header is **validly signed**, **currently valid**, **bound to exactly
that action and target**, and **not previously used**.

- **Target break** — make the target act on a request whose token is absent, forged, expired,
  replayed, altered, or bound to a different action/target.
- **Sidecar break** — make the sidecar return `ALLOW` for a request that is not a currently-
  valid, correctly-bound, single-use, validly-signed token.

Using a real token once, as intended, is **not** a break — that is the gate working. A read-only
inspector (`IMPLEMENTATION/envelope_inspector.py`) adjudicates a token the way the target does;
self-check before you submit.

## Out of scope (by design — not vulnerabilities)

- Denial of service, flooding, or availability — refusing is the design, not a break.
- Acting on a genuinely valid, unused token — that is correct behavior.
- "An authorized action could be unwise" — the gate checks authorization, not wisdom.
- Stealing the signing key, or compromising the host OS / cloud / TLS by means outside the
  request protocol. These are welcome as separate, credited infrastructure reports.

## Coordinated disclosure & credit

Coordinated disclosure with a **90-day** fix window. Confirmed findings are credited — by name
or handle, your choice — in the repository, in the project's public verification ledger, and,
where applicable, via a CVE and acknowledgment in the next Zenodo Enforcement-Evidence Addendum.

## Live testing & safe harbor

A public four-node test surface exists, and a **private, invite-only** credited engagement is
run directly by the maintainer. Authorized testing of the live surface is governed by a
safe-harbor clause (`deploy/SAFE_HARBOR_CLAUSE.md`) that is being **finalized with counsel**; no
testing of the live hosts is authorized until that clause is signed and you have received an
explicit engagement authorization. Testing the open-source code locally needs no authorization.

## Honest scope

Elyon-Sol has **not** yet been validated by any external party. Every test and review to date is
the maintainer's own; internal review is not external validation. A confirmed external break
would be the first such result, and a run that finds nothing is recorded as exactly that — never
as "unbreakable."
