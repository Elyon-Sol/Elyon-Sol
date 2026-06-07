# 12 - G5 real-transport design and build plan

Repo path: docs/restructure/12_g5_transport_design.md

Status: DESIGN / PLAN. No code, canon, manifest, spec, or test change is made by
this artifact. It is the G5 counterpart of 08_enforcement_design.md: a design
that precedes a build, written against the code on disk at HEAD 0c1ac4b
(source-first). Confirm every file:line reference against the live tree before
acting on it; this artifact is a map, not the territory.

Governance: this is a design artifact, not an evidence claim. Per GR-3 and
Lesson 10, nothing here is validated by a model judgment of soundness or value;
the only thing that closes G5 is a referent-bound result (a runnable attack
passing or failing against a real surface, ultimately run by an external
attacker). See docs/methodology/external_verification_readiness.md.

Verified env capability (spike, 2026-06-06, referent-bound): the build sandbox
supports real TLS sockets between distinct OS processes with fail-closed cert
verification (a trusted CA bundle is honored; an untrusted self-signed peer
raises SSLError), Python 3.10 + cryptography + requests + the openssl CLI. It
does NOT have docker / docker-compose, and it is a single host. Consequence for
the build order below: the in-env proof of steps 1-5 runs over plain
multi-process + TLS on one host; the docker-compose and two-real-VM artifacts
(step 2) are deploy-target deliverables, validated only when run on real hosts,
never greened in-env.

---

## 1. What G5 is, and the two finish lines

G5 = real cross-host transport, so that there is a live external surface to
attack rather than a loopback simulation. The current chain already runs
end-to-end (the three deployment predicates are green in EVIDENCE/readiness.json),
but every "transported" / "exercised_e2e" proof is loopback-modeled, and the
gate-to-target hop is monkeypatched in the runners. The readiness manifest is
honest about this: each predicate's blocked_by note explicitly excludes "true
multi-machine / TLS (the named G5 floor; deployment)."

Keep two finish lines separate, because conflating them is the trap (section 6):

- (A) A G5-READY BUILD. Code that, run on real hosts, performs real cross-host
  TLS transport with a real downstream policy, plus a harness that fires real
  attacks at it. FULLY BUILDABLE by author + model. This artifact plans (A).

- (B) G5 CLOSED. The predicate is green because the system WITHSTOOD attack on a
  real surface, run by an EXTERNAL attacker. NOT promptable, NOT buildable
  in-loop: closing it with author-written attacks run by the author is dev QA-ing
  its own build, which GR-3 catches. The build gets us to (A); operating it plus
  an external attacker closes (B).

The honest framing this rests on (from external_verification_readiness.md):
development plus dev-side verification is DONE (the 203-test suite is the dev-side
suite). QA = external validation has not started and cannot start until there is
a real surface, because a stranger cannot meaningfully attack a loopback
simulation. Gate 1 of the external-readiness criterion (attackable deployment
over real transport) is the load-bearing gate and it gates the rest.

---

## 2. The buildable vs external split

| Piece | Build (author + model) | Run / certify (external) |
|---|---|---|
| Multi-node + TLS infra | write the compose / transport / cert setup | author operates it (ops hat) |
| Real downstream policy | write a reference enforcing target (NOT authored-to-pass) | a target the author did not write |
| Attack harness | write the break-it toolkit | (scaffolding only) |
| The attacking | (not buildable) | a STRANGER; the actual referent |

Everything in the left column is in-loop buildable: the model writes the code,
the author runs it. The right column is the author's to arrange, and the
attacking is the only thing that actually closes G5.

---

## 3. Where the code is today (the seam, source-first)

The transport-relevant surfaces at HEAD, and what each does now:

- Gate-to-target push. IMPLEMENTATION/pep.py governed_call (line 125) forwards
  on ELIGIBLE via requests.post to body["target_url"] (line 276), attaching the
  signed envelope as the out-of-band header X-Elyon-Sol-Envelope (line 279). This
  hop is already a real HTTP client call; it is only ever faked in the runners
  (fake_post in g5_signed_cross_host_001_runner.py line 187), not in production
  code. To go cross-host this needs a real target listening, and TLS.

- Published-record fetch. IMPLEMENTATION/published_source.py
  fetch_published_record (line 131) does requests.get over loopback (line 152),
  then load_record_from_bytes (line 94) anchor-verifies the bytes against a
  pinned root sha256 (anchor_sha256, line 84) before parsing. This is already a
  real HTTP client; the loopback constraint is in how it is SERVED, not how it is
  fetched (see below). The trust bootstrap (Decision B-prime-1, pinned root hash)
  and the named G5 floor (secure anchor distribution, TLS, true multi-machine)
  are documented in that module's header (lines 15-35).

- Record serving. There is no publisher server module. The published record is
  served only by an ephemeral http.server started inside the runners (_serve in
  g5_signed_cross_host_001_runner.py line 93). A real deployment needs a standing
  publisher endpoint over HTTPS.

- Target-side verification. IMPLEMENTATION/verifier.py verify_envelope (line 196)
  is delivery-agnostic and already accepts a fetched record_source (line 200),
  pinned_public_keys / key_record_view, and now (for expiry). It is complete and
  reused as-is. What is missing is a server that CALLS it.

- The reference target. IMPLEMENTATION/target.py is a trivial stub (8 lines: it
  prints and returns {"status": "EXECUTED"} with no verification). The actual
  enforcing-target logic exists only as embedded scaffolding: the TARGET_DRIVER
  subprocess string in g5_signed_cross_host_001_runner.py (line 118) and the
  enforcing target inside TESTS/adversarial/test_enforcement.py. There is no
  standalone, deployable enforcing target. This is the single largest "named not
  built" item for (A).

- The published-record generators. EVIDENCE/published_hashes_gen.py (committed
  record), EVIDENCE/published_keys_gen.py and EVIDENCE/published_roots_gen.py
  (runtime artifacts, never committed) generate the records the publisher would
  serve. They exist and are reused as-is; the gap is serving their output over a
  real endpoint.

The seam summary: the two HTTP CLIENTS (gate push, record fetch) are real
already. The two SERVERS (the enforcing target, the record publisher) exist only
as test/runner scaffolding. TLS and multi-host networking wrap both. G5 (A) is
mostly "promote the scaffolding servers to real services and put TLS + real
network around the existing clients," not "rewrite the trust logic."

---

## 4. The trap (the same disease, one layer out)

Building infra + reference target + harness, running your OWN attacks, and
recording "QA passed" is dev QA-ing its own build with attacks it designed. It is
inflated for the identical reason the cross-model evaluates were (shared
authorship of the thing and the test of the thing). Real TLS and real nodes do
NOT fix this; only the ATTACKER being external does. The harness's value is
scaffolding for the stranger, not a verdict. Build (A) and (B) explicitly TOWARD
handing off to an external attacker (C). Per GR-3, any attack result produced
in-loop is class-(a) characterization at most ("this specific attack, as I wrote
it, was refused"), never certification that the surface is secure.

---

## 5. Build order (each step a runnable deliverable)

Each step is build-then-wire (the project's discipline since VL-025): build the
capability with no default-path behavior change, prove it with a runner, wire it
only when the step that needs it lands. None of these steps should change pep.py's
admission logic, the verifier logic, the canon, or any existing test's meaning;
they add a real transport substrate around the existing logic.

### Step 1 - Transport interface seam (single-box or cross-host, same code)

Goal: one clean interface so the same gate / target / publisher code runs on a
single box (dev) or across hosts (real), with the only difference being
configuration (addresses, certs).

- Factor the gate-to-target push so target_url can be an https:// URL with a
  configured CA / verification policy, and the requests.post call honors it.
  Today the call is hard-coded with timeout=10 and no TLS configuration
  (pep.py line 276); add a transport-config seam (verify=<ca bundle or True>,
  optional client cert) without changing the body or the header contract.
- Factor record serving behind a small publisher interface so the same record
  bytes can be served by the runner's http.server (dev) or a standing HTTPS
  service (real). The fetch side (published_source.fetch_published_record)
  already takes a publisher_url and pinned_root and needs no change beyond
  allowing https:// and a TLS-verification argument.

Deliverable: a transport-config module (proposed IMPLEMENTATION/transport.py or
config additions) plus a runner that exercises the existing chain through the new
seam single-box, proving byte-identical behavior to the current loopback runner.
No default-path change.

### Step 2 - Two-node harness (off the laptop)

Goal: make the chain run as separate processes on separate network endpoints,
first via docker-compose, with notes for two real VMs / cloud instances.

- NOTE (verified): docker / docker-compose is NOT available in the build
  sandbox, so this step's compose file cannot be greened in-env. In-env, "two
  nodes" is proven as separate OS PROCESSES on one host over real TLS sockets
  (the spike confirmed this substrate works); the docker-compose.yml and the
  two-real-VM notes are deploy-target artifacts validated only on real hosts.
- docker-compose with three services: gate (node A, runs pep.py),
  target (node B, runs the reference enforcing target from step 4),
  publisher (serves the published_* records over HTTP first, HTTPS in step 3).
- The gate forwards to the target over the compose network; the target fetches
  the published record from the publisher over the compose network; nothing is
  monkeypatched, no subprocess-with-shared-tree shortcut (contrast the current
  runner, which copies the repo into a temp dir and runs the target as a
  subprocess of the same machine).
- Provide notes (not just compose) for promoting node A and node B to two real
  machines, since "real hosts, real network" is the actual G5 floor and
  compose-on-one-host is still a partial model.

Deliverable: docker-compose.yml + a two-node runner/script that drives a call
through gate -> target -> publisher across the compose network and records
honor/refuse, plus a README for the two-real-VM promotion.

### Step 3 - TLS / cert setup and the trust bootstrap

Goal: real certificate verification on both HTTP hops, and an explicit,
out-of-band trust bootstrap at the pinned anchor.

- Cert generation (a real-ish CA so certs verify), the publisher and target
  served over HTTPS, the gate and target configured to verify.
- The pinned published-record anchor (anchor_sha256 of the served record) is
  distributed to the target OUT-OF-BAND (configuration), never fetched alongside
  the record (that would be circular - published_source.py header, lines 22-27).
  Document the distribution as a manual, out-of-band step; per Decision F and the
  external-readiness gate 5, secure distribution of the anchor itself is a NAMED
  FLOOR, acknowledged not defended.
- Where the design wants key pinning (the gate signing public key, the publisher
  root), pin it as out-of-band configuration consistent with the existing
  out-of-band pin in the cross-host runners.

Deliverable: cert-generation scripts + TLS-enabled compose + a runner proving the
chain works over verified TLS, with the anchor / key pins supplied out-of-band.

### Step 4 - Reference downstream enforcing target

Goal: a standalone, deployable enforcing target that honors or refuses by its OWN
policy reading the envelope - explicitly NOT authored-to-pass.

- Promote the embedded TARGET_DRIVER logic (g5_signed_cross_host_001_runner.py
  line 118) into a real service (replacing or superseding the target.py stub):
  read X-Elyon-Sol-Envelope from the request header; fetch the published record
  from the publisher; pin the gate signing key and the publisher anchor
  out-of-band; call verify_envelope(envelope, interaction, target_url,
  record_source=<fetched>, pinned_public_keys / key_record_view=...); execute
  iff accepted, refuse (403) otherwise.
- Write it as a REFERENCE policy: its acceptance criterion is "verify_envelope
  accepts AND the published record's pins match the committed record" (the
  Decision-C anchor used in TESTS/adversarial/test_enforcement.py), not "make the
  author's happy-path call pass." The distinction matters for (B): a target the
  external attacker can point at must not be tuned to the author's test vectors.
- The A1 adversary (a caller that never routes through the gate, reaching the
  target directly) is closeable ONLY by this target's own policy of refusing
  un-attested calls, not by the gate (verifier.py lines 67-72; artifact 08
  section 4.4). State this in the target's docs as a named boundary.

Deliverable: IMPLEMENTATION/<reference target server> + a runner showing it
honoring a valid routed call and refusing forge / replay / target_url-swap /
absent-envelope / record-mismatch over the step-2/3 transport.

### Step 5 - Attack harness mapped to the claim sheet

Goal: turn external_verification_readiness.md gate 2 (the falsifiable claim
sheet) into runnable attacks against the LIVE nodes, each emitting a clear
pass/fail (refused / admitted).

Map each claim-sheet challenge to a runnable attack against the step-2/3 surface:

- A1 bypass: reach the target directly without routing through the gate. Expected:
  refused by the target's un-attested-call policy (step 4); honestly flagged as
  target-policy-defended, not gate-defended.
- Keyless forge on the signed path: present an envelope with no issuer signature.
  Expected: REF_VERIFY_SIGNATURE_INVALID (defended by sign/verify;
  signing_forgery_defeated_001_runner.py is the in-process precedent).
- Revoked / out-of-window issuer key: Expected REF_VERIFY_KEY_REVOKED /
  REF_VERIFY_KEY_OUT_OF_WINDOW (key-record gate).
- Key record signed by a revoked / retired root: Expected REF_VERIFY_ROOT_REVOKED
  / REF_VERIFY_ROOT_RETIRED (root gate).
- Verbatim replay and target_url-swap: Expected REF_VERIFY_BINDING_MISMATCH
  (binding check; test_verifier / test_findings_001 are the in-process
  precedents).
- Mint acceptance despite a byte-divergent target disk: the cross-host fetch
  property, but over REAL transport per gate 1, not loopback (the current
  g5_signed_cross_host runner proves this at loopback).
- Stale-but-anchor-matching record (the A3b freshness sub-class): a validly signed
  stale record is still honored today (readiness.json END_TO_END note;
  g5_signed_cross_host_001_runner.py lines 53-60). The harness should include this
  as an OPEN attack the surface does NOT yet defend, stated honestly, not hidden.

Deliverable: an attack-harness package (proposed TESTS/attack/ or a top-level
harness dir) where each attack is a script returning pass/fail against the live
nodes, plus a claim-sheet document pairing each bounded claim with its attack and
the current honest status.

---

## 6. Relationship to the readiness predicates

The three deployment predicates are green at loopback and their blocked_by notes
already exclude true multi-machine / TLS. Steps 1-5 do not retroactively change
those predicates' meaning; the real-transport surface is a STRONGER referent than
the loopback proofs that currently back them. Two honest options for recording
the new tier, to be decided when step 2/3 lands (not now):

- (a) Strengthen the existing predicates' proof-of-record from the loopback runner
  to the real-transport runner, keeping the predicate names.
- (b) Add a distinct REAL_TRANSPORT (or similar) predicate, leaving the loopback
  predicates as the in-process regression floor and the new one as the deployment
  floor.

Either way, per GR-2 (readiness is test-derived, never human-attested) the new
flag must name a passing real-transport proof or be false with a reason. And per
the external-readiness criterion, even a green real-transport build is finish line
(A); G5 CLOSED (B) still requires the external attacker.

---

## 7. What this does NOT change, and the standing bounds

- No new canonical invariant (canon section 14): the gate still decides and
  delivers; the target verifies and acts or refuses; transport is verification
  I/O. This is the same posture published_source.py and verifier.py already hold.
- The named floors beyond the gate are unchanged: out-of-band root / issuer
  COMPROMISE recovery (a trust-model limit, not closeable by attack); secure
  distribution of the pinned anchor; the A1 caller (target-policy-defended, not
  gate-defended); the A3b freshness sub-class (