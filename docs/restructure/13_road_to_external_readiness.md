# 13 - Road to external readiness (local directive)

Repo path: docs/restructure/13_road_to_external_readiness.md
Status: DIRECTIVE / PLAN. Establishes the ordered local (in-house) work that takes the
repository to the point where EXTERNAL work (an attacker / reviewer on a real surface) can
begin, with the code and ledger as clean as we can make them. Created VL-067.

## Goal and definition of done

External validation is the load-bearing, still-zero axis (VL-066 evaluation; GR-3;
`docs/methodology/external_verification_readiness.md` gate 1: an attackable real-transport
deployment gates everything else). This directive does NOT perform external validation - that
requires a real external party and is the author's to arrange. It performs every LOCAL item
that must precede it.

DONE for this push = all of:
- (A) the base is clean: no dead modules, the gap tracker and STATE prose reflect reality,
  the suite + runners run in CI, and the deposit-readiness audit is recorded.
- (B) the wedge is hardened as far as in-house work allows: record freshness, clock-skew
  tolerance, a shared-replay-cache seam, a real MCP integration, and a latency budget.
- (C) an attackable real-transport surface exists as deployable artifacts: deploy packaging,
  real TLS/cert + trust bootstrap, and an attack harness + falsifiable claim sheet.

Validation locus is stated per item: SANDBOX = can be greened in the build sandbox;
AUTHOR = produced in-house but validated only on real hosts/CI/hardware (the sandbox has no
docker, is single-host, and has no real CA).

Out of scope (not local code): G12 / G13 canon-layer halves - blocked on a canon-version
event under GR-1; and the section-14 caller-carry / proxy-removal fork - an optional
architecture, deferred.

---

## Phase A - clean the base (do first; low risk, reduces drift)

- **A1. Retire the `target.py` stub.** Remove `IMPLEMENTATION/target.py`; the VL-061
  reference enforcing target supersedes it (no code importer). Update README/artifact-01 tree
  references. Acceptance: file gone, grep-clean, suite green. Locus: SANDBOX.
- **A2. Retire `server.py`.** The named dead-module cleanup. Confirm no importer, remove,
  update doc tree references. Acceptance: gone, grep-clean, suite green. Locus: SANDBOX.
- **A3. Refresh the gap tracker.** Update `04_current_vs_claimed.md` G4 (defensibly
  non-bypassable for routed-and-attested; A1 closed by the reference target) and G5 / the A3b
  sub-cases to reflect VL-061/063/065/066. Acceptance: statuses match the ledger. Locus: SANDBOX.
- **A4. Clear the prose-drift.** Fix STATE.md's stale numbered "Next open action" list and the
  stale "T-bookkeeping (G1/G8/G9/G11/G14 ...)" label (G1/G11/G14 are RESOLVED). Acceptance:
  no stale gap labels in STATE prose. Locus: SANDBOX.
- **A5. CI.** Wire the pytest suite and the exit-coded EVIDENCE runners into CI so green is
  enforced automatically (closes the G8 residual). Acceptance: a CI config that runs the suite
  + runners on push. Locus: AUTHOR (runs in the real CI).
- **A6. Deposit-readiness audit (VL-059, reserved).** The GR-3-bound audit of what is
  deposit-ready vs bounded/named-open. Acceptance: a recorded audit; no overclaim enters any
  deposit. Locus: SANDBOX (analysis).

## Phase B - harden the wedge as far as in-house allows

- **B1. Record freshness (A3b sub-case b).** Promote the published-hashes record from the
  byte-anchor model (B-prime-1) to the signed-record model (mirror `key_record_source.py`):
  publisher signature under a stable pinned key + `not_after` + monotonic `serial`; the reader
  enforces freshness (`REF_VERIFY_*_STALE`). Acceptance: a failing test (stale record honored)
  flips to refused; suite green. Locus: SANDBOX.
- **B2. Cross-host clock-skew tolerance.** Add a configurable skew window to the freshness
  checks (decision and record) with an explicit NTP assumption documented. Acceptance: tests
  for in-window/out-of-window with skew; suite green. Locus: SANDBOX.
- **B3. Shared-replay-cache seam.** Factor the reference target's seen-set behind a small
  interface (in-memory default; a shared/TTL backend pluggable) so a multi-instance executor
  can share replay state. Acceptance: the interface + the in-memory impl tested; a documented
  adapter point for a shared store. Locus: SANDBOX (seam); AUTHOR (real shared store).
- **B4. Real MCP server integration.** Promote the in-process wedge demo to a real MCP
  `tools/call` server (initialize handshake + the admissibility gate on tool execution).
  Acceptance: a runnable MCP server refusing un-admitted / replayed / drifted / stale tool
  calls. Locus: SANDBOX (server runs locally).
- **B5. Latency / throughput budget + ergonomics.** Measure added p50/p99 verify latency and
  package integration as a thin middleware/SDK. Acceptance: a recorded latency proof + a
  few-line integration example. Locus: AUTHOR (representative hardware) for the numbers;
  SANDBOX for the SDK.

## Phase C - external-readiness scaffolding (the prerequisites to the attack line)

- **C1. Deploy packaging.** A docker-compose (gate / reference target / publisher as networked
  services) + a two-real-host / cloud runbook. Acceptance: compose + runbook committed; a
  documented stand-up. Locus: AUTHOR (docker absent from the sandbox; validated on real hosts).
- **C2. Real TLS/cert + trust bootstrap.** Promote the local test-CA to real certs (real CA /
  Let's Encrypt) + an out-of-band anchor/key distribution runbook. Acceptance: cert scripts +
  runbook; the chain verified over real TLS. Locus: AUTHOR (real hosts).
- **C3. Attack harness + falsifiable claim sheet.** Turn the wedge claim and
  `external_verification_readiness.md` gate 2 into runnable attacks, each emitting pass/fail
  against a live surface, with the claim sheet pairing each bounded claim to its attack and
  current honest status (including known-open: record freshness if B1 not yet landed, A3b,
  root-compromise). Acceptance: the harness + claim sheet committed; runs against the C1/C2
  surface. Locus: SANDBOX (scaffolding); AUTHOR (against the live surface).
- **C4. Real-transport readiness predicate.** When C1-C3 land, record the new tier in
  `EVIDENCE/readiness.json` per artifact 12 section 6 (strengthen the existing predicates'
  proof-of-record to the real-transport runner, or add a `REAL_TRANSPORT` predicate).
  Acceptance: GR-2-honest predicate naming a passing real-transport proof. Locus: AUTHOR.

---

## Sequencing and gating

A -> B -> C is the default order (clean base, then harden, then deploy/scaffold). Strict
prerequisites for an external ATTACK are the Phase-C items plus standing up real hosts;
Phase B maximizes preparedness but most of it is not a hard blocker (record freshness becomes
a claim-sheet line; the shared cache only matters multi-instance; MCP/latency gate the
customer axis). Each item lands as its own VL increment (build-then-wire, referent-bound,
no canon/hashed-file change unless explicitly scoped), so a fresh session can take the top
unfinished item from this directive without reconstructing context.
