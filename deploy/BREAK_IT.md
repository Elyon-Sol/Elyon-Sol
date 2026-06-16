# Break Gargoyle - open challenge

DRAFT - public recruiting asset, uncommitted. This is the ONLY document an
external attacker receives (the decontaminated pack, Gate 4). It contains no
internal framing: no design rationale, no test results, no confidence claims, no
project history. Keep it that way - do not publish the repo, the canon, the
ledger, or any cross-model result alongside it. Have counsel review the safe-
harbor / authorization wording before this goes public. Fill the <bracketed>
placeholders before publishing.

---

## The challenge

We run a gate that decides whether an action is allowed to happen BEFORE it
happens, and refuses anything that does not carry a valid permission to act. We
think you cannot make it act on something it should not. We would like you to try.

A confirmed break is a real result and we will credit and publish it. We are not
claiming this is unbreakable - we are asking you to find where it is.

## What we claim (the thing to disprove)

The target service performs an action ONLY if the request carries a Gargoyle
eligibility token (the `X-Elyon-Sol-Envelope` header) that is all of:

- validly signed by the gate's key (which you do not have),
- currently valid (not expired or stale),
- bound to exactly that action and that target,
- not previously used (each token is single-use).

Our claim: without the gate's signing key, there is no request you can craft that
(a) makes the target perform an action, or (b) makes the eligibility sidecar
answer ALLOW, outside those four conditions. Using the system as intended (getting
a real token from the gate and presenting it once) is not a break - that is it
working. A break is making it act, or allow, when one of the four conditions does
not hold.

## The live targets

- Target (the thing that acts):      https://target.elyon-sol.io:9443
- Gate (mints/signs tokens):         https://gate.elyon-sol.io:8443
- Eligibility sidecar (allow/deny):  https://authz.elyon-sol.io:9243
- Publisher (serves the record):     https://pub.elyon-sol.io:9143

## What counts as a break

Reproduce either, with steps we can re-run:

1. TARGET break - get the target to perform an action (it exposes a count of
   actions performed at `GET /received`; an increment is proof it acted) in
   response to a request whose token is absent, forged, expired, replayed, altered,
   or bound to a different action or a different target.

2. SIDECAR break - get the eligibility sidecar to return HTTP 200 / `ALLOW` for any
   request that is not a currently-valid, correctly-bound, single-use, validly-
   signed token.

A break must be reproducible by us from your steps. One reproduction beats any
description.

## What does NOT count (please don't spend time here)

- Taking it offline / denial of service / flooding. It is designed to refuse when
  it cannot be sure; making it refuse or making it unavailable is not a break.
- Stealing the gate's signing key, or compromising the host OS, cloud account, or
  TLS certificate by means outside the request protocol. If you obtain the signing
  key you can of course sign - that is a key-custody question, not a protocol break.
  (Infrastructure findings are still welcome as SEPARATE reports - credited - they
  just are not breaks of the claim above.)
- Getting it to act on a request that carries a genuinely valid, unused token. That
  is correct behavior.
- Pointing out that a validly-authorized action could be used for something
  unwise. The gate checks whether an action is authorized and attested, not whether
  an authorized action is a good idea. That is out of scope by design.

## Rules of engagement

- Test ONLY the four hosts listed above. Nothing else is in scope.
- No denial-of-service or volumetric testing. No social engineering or phishing of
  the operator or any person. No attacks on other systems, tenants, or networks.
- Report privately first (see below). Please allow <DISCLOSURE WINDOW, e.g. 30
  days> for a fix before any public disclosure; we will coordinate timing and
  credit with you.
- Safe harbor: good-faith security research conducted within this scope and these
  rules is authorized; we will not pursue action against testing that stays within
  them. <Have counsel finalize this clause.>

## How to interact (enough to start)

1. A legitimate, allowed flow (so you can see what "valid" looks like): ask the
   gate to mint a token for a sample action -
       POST https://gate.elyon-sol.io:8443/governed-call
       body: {"target_url": "https://target.elyon-sol.io:9443/target",
              "interaction": { ... sample action ... }}
   The response carries the signed token. Present it once to the target (in the
   `X-Elyon-Sol-Envelope` header) or to the sidecar - it is honored once.
2. Then attack the edges: drop the header, alter any field, present it twice,
   present an expired one, point it at a different action or target, fabricate one,
   etc.
3. Self-check tool: the inspector CLI at <link to inspector + usage> tells you how
   the gate reads a given token, so you can confirm whether you actually got a break
   before submitting.
4. Full request/response shapes and the sample action are at <link to a short
   "how to interact" appendix>.

## How to submit

Send to <CONTACT - security@elyon-sol.io or a form link>:
- the break category (target / sidecar / infrastructure),
- exact reproduction steps (request(s), headers, order, timing),
- what you observed (status codes, the `/received` count, response headers).

We reproduce, classify, and respond. Every confirmed break is credited to you (or
anonymously, your choice) and published as either a fix or a documented limit.

## Reward

<REWARD - decide before publishing. Example tiers:>
- Confirmed target or sidecar break: <$amount>, by severity / novelty.
- Confirmed infrastructure finding (out-of-scope of the claim, still real): <$amount
  or credit>.
- Duplicate or already-known: credit, first reporter noted.
Credit-only is also a legitimate model for a first run; decide and state it here.

## What we do with the result

A confirmed break becomes a fix or a documented limit, with your credit. A run
that finds nothing is recorded as "not broken within this scope and this window" -
never as "unbreakable." We are looking for the edge, honestly. Thank you for
looking with us.
