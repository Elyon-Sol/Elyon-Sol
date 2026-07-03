# Elyon-Sol — Wall of Fame

> **Status: nobody has broken it yet.** Be the first.

This is the public scoreboard for the Break-Elyon-Sol challenge. Every confirmed finding
is recorded here permanently, by name or handle, at the finder's choice — and mirrored into
the project's verification ledger (`EVIDENCE/verification_ledger.md`), which is the
project's record of record, forever.

## First blood

_Open._ The first person to make the target act — or the sidecar say ALLOW — on a call the
claim sheet says must be refused takes this line, permanently.

| # | Finder | Date | Class | Finding (one line) | Ledger | Status |
|---|--------|------|-------|--------------------|--------|--------|
| — | _open_ | —    | —     | _first confirmed break lands here_ | — | awaiting |

## Honorable mentions (real issues, outside the core claim)

Defense-in-depth notes, doc bugs, infra observations, and guarantee-weakeners that don't
rise to a full break — still credited.

| Finder | Date | Note | Credit |
|--------|------|------|--------|
| _open_ | —    | —    | —      |

---

## How this is scored (the CTF rules)

**The dare:** we run a gate that refuses any action without a valid permission to act. We
think you cannot make it act on something it shouldn't. Prove us wrong.

**A capture =** a working, reproducible exploit that causes the target
(`target.elyon-sol.io`) to act — its `GET /received` count increments — on a request whose
token is absent, forged, expired, replayed, altered, or bound to a different action/target;
**or** causes the sidecar (`authz.elyon-sol.io`) to return `200 / ALLOW` for a request that
is not a currently-valid, correctly-bound, single-use, validly-signed token.

**Not a capture** (these confirm limits we already publish, and we say so up front): DoS or
flooding, stealing the signing key or compromising the host/CA outside the request
protocol, or acting on a genuinely valid unused token (that's it working).

**Self-adjudicated:** confirm your capture with `INSPECT_YOUR_BREAK.md` before submitting —
the inspector tool decides, not the author. Start in 60 seconds with
`BREAK_IT_IN_60_SECONDS.md`.

**The flag is your name.** No cash — the reward is durable: first-blood on this wall, a
permanent named entry in the public ledger, co-credit on the next Zenodo record (with your
ORCID), a CVE where applicable, an invitation to author the fix, and a founding red-team
seat. Details in the site's Red-Team section.

Submit: **security@elyon-sol.io**.
