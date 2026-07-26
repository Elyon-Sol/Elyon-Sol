# Security Policy

> **Paused — 2026-07-20.** Active development is paused, not ended — the author may resume it. The public test nodes are offline. The
> credited red-team challenge is **closed** — there is no live public surface, no active engagement,
> and no CVE / safe-harbor program for one. You can still stand up the open-source surface yourself
> and test it ([`deploy/SPIN_UP_YOUR_OWN.md`](deploy/SPIN_UP_YOUR_OWN.md)); a genuine security report
> is still welcome at the address below and handled best-effort.

Elyon-Sol is a deterministic, fail-closed admission gate. Its entire value is that it
refuses actions that are not authorized — the core admissibility claim below still describes what
the code does, and you can verify it against a self-hosted instance.

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

## Reports (project retired)

The project is retired, so the former credited-challenge mechanics — the 90-day coordinated-
disclosure window, ledger / CVE credit, and acknowledgment in a next Zenodo Enforcement-Evidence
Addendum — are wound down. A genuine security report is still welcome at the address above and
will be handled on a best-effort basis.

## Testing (self-host)

The four-node public test surface is **retired**; there are no in-scope live hosts. The whole
admission surface is open source — stand it up locally
([`deploy/SPIN_UP_YOUR_OWN.md`](deploy/SPIN_UP_YOUR_OWN.md)) and test your own instance; testing
the open-source code locally needs no authorization. There is no live public surface, and
therefore no safe-harbor program for one.

## Honest scope

Elyon-Sol was **never** validated by any external party. Every test and review was the
maintainer's own; internal review is not external validation. No confirmed external break was ever
recorded — external validation was the single finish line the project never reached.
