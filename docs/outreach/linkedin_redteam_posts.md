# LinkedIn posts - red-team solicitation (paste-ready)

Channel decision (VL-127): red-team solicitation runs on LinkedIn + the public one-page
site; NO bug-bounty platform. Every post leads with the same three things (per
deploy/SOLICITOR_INTAKE_CHEATSHEET.md): the one-line claim to disprove, the
recognition/ownership model (not cash), and the intake address. All interest routes to
security@elyon-sol.io; access stays invite-only, vetted, and papered with a signed
Authorization-to-Test. Posts carry the honest-scope line (no external validation has
occurred yet - this challenge is the attempt to obtain it) and never include internal
confidence, test results, or cross-model verdicts (VL-057).

PUBLISHING IS GATED: do not post until the PHASE1_PRELAUNCH_RUNBOOK gates are green -
counsel-approved safe harbor (HARD GATE) included. Drafts only until then.

Fill before posting: [SITE URL] = the live one-pager address.

---

## Post 1 - the challenge (primary)

I built a security gate, and I'm asking you to break it.

Elyon-Sol is a deterministic, fail-closed admission gate for machine-initiated actions
(think: AI agents calling tools). Every admitted call carries a signed, single-use
"admissibility envelope" cryptographically bound to exactly that action and that
target; the target re-verifies it before acting.

The claim to disprove: without the gate's signing key, there is no request you can
craft that makes the live target act - or the authorization sidecar answer ALLOW -
unless the token is validly signed, currently valid, bound to exactly that action and
target, and not previously used.

The test surface is live, public, and runs under real TLS. Nobody outside the project
has validated this yet - that is exactly what this challenge exists to change, and why
a confirmed break is a real, credited result: a permanent named entry in the public
verification ledger, co-credit on the Zenodo record (your ORCID), a CVE where
applicable, invited fix-authorship, and a founding red-team seat. No cash bounty -
durable credit and ownership.

The engagement is private and invite-only. Email security@elyon-sol.io with a short
note on your background. Scope, rules, and the formal spec: [SITE URL] - DOI:
10.5281/zenodo.21107731

#appsec #redteam #cryptography #AIagents #AIsafety #security

---

## Post 2 - mission-aligned (AI-governance / safety audience)

How do you make an AI agent's actions verifiable - not "logged", verifiable?

Elyon-Sol is my attempt at one load-bearing piece: a deterministic admission gate that
refuses any machine-initiated action that does not carry a valid, signed, single-use
permission bound to exactly that action. Fail-closed by construction: on any doubt or
any exception, the action does not happen. The spec is formal (canon v0.9.8.4), the
implementation is open (AGPL), and a four-node test surface is live under real TLS.

Honest status: the refusal properties hold against every in-house and cross-model
attack we have thrown at them - but no EXTERNAL party has validated the system yet,
and internal evidence is not external validation. So this is a recruiting post: I am
looking for security researchers and protocol/crypto people to try to break it, as a
private, invite-only, safe-harbor-backed engagement. A confirmed break is credited
permanently and by name in the project's public verification ledger, with Zenodo
co-credit, CVE where applicable, and fix co-authorship - the point is a public good
with your name on it, not a bounty payout.

Interested, or know someone who would be? security@elyon-sol.io - details: [SITE URL]

#AIsafety #AIgovernance #verifiableAI #appsec #formalmethods

---

## Post 3 - short follow-up / reshare

Still standing: nobody has yet made the Elyon-Sol gate act on a call it should refuse.
The challenge is live, the surface is public, and the first confirmed break gets its
finder a permanent named place in the project's verification record. Fresh eyes
wanted - security@elyon-sol.io - [SITE URL]

#redteam #appsec

---

## Comment/reply discipline

- Answer operational questions (is the endpoint up, wire shape) in comments; never
  explain the design, defend a refusal, or hint at attack paths (artifact 29, 4.4).
- Anyone asking for access: route to security@elyon-sol.io, no exceptions, no scope in
  comments.
- Never state or imply external validation exists until a G5 referent is ledgered.
