# Verification ledger - curated index

**This is a navigation aid, not the record.** The authoritative record is
`EVIDENCE/verification_ledger.md`, which is append-only and immutable (GR-4). This
index is ADDITIVE (GR-4 clause 3): it points at entries, never replaces them, and is
regenerated - never used to justify removing anything from the ledger. When this index
and the ledger disagree, the ledger wins.

**Archived (GR-5).** As of 2026-07-03 the ledger is split into immutable volumes:
VL-001..VL-107 live in `EVIDENCE/ledger_archive/vol_001__VL-001_to_VL-107.md`; VL-108
onward stay in the active `verification_ledger.md`. This index spans BOTH. Reconstruction
manifest: `EVIDENCE/ledger_archive/INDEX.md`.

Two views: the load-bearing entries grouped by theme (for orientation), then the full
chronological list (every entry, by its own title).

---

## A. Load-bearing entries (curated)

### Foundations & method
- **VL-001** - ledger established.
- **VL-006** - canon v0.9.8.4 transcribed and locked.
- **VL-008** - cross-model verification method: task-to-source binding is the operative variable.
- **VL-057** (+ follow-ups) - referent-binding; cross-model "convergence" demoted from evidence to framing stress-test (basis of GR-3).
- **VL-067** - directive: the road to external readiness (artifact 13).
- **VL-103** - the G5 external-validation execution plan.

### Anchor findings & gap closes
- **VL-002** - G0: CCS specification/implementation drift (the anchor finding).
- **VL-012 -> VL-029** - G0 closed: rename half (VL-012), build half (VL-029).
- **VL-019** - G2 closed in code (schema validator wired).
- **VL-034** - G7 closed (canon-derived tests, both domains).
- **VL-053 / VL-054** - G11 / G14 closed.

### The cryptographic / trust floor
- **VL-038** - G4 enforce: a defensible refused bypass (target verifies against the published record).
- **VL-040** - issuer signing; the forgery finding closed on the signed path.
- **VL-041 / VL-042 / VL-044** - key expiry; published signed key-record + revocation; root recovery.
- **VL-047 / VL-048 / VL-049** - the three readiness predicates go green (DEFAULT_SECURE, END_TO_END, ROOT_RECOVERY).
- **VL-065 / VL-066** - decision freshness; replay / exactly-once + the wedge property end-to-end.

### The governance substrate (built, largely not deployed)
- **VL-113 -> VL-116** - Feature 1 (impact classification -> grant -> pep wiring -> audit); mechanism complete.
- **VL-117 / VL-118** - Feature 2 mTLS client-auth proof; the integration proof (the two features compose).
- **VL-119 / VL-120** - residuals R1 (approver provenance/role) and R2 (shared store under scale).
- **VL-123** - white-box hardening cluster (governance_wiring startup guard).

### The live surface & external readiness
- **VL-073** (+ follow-ups) - CI green (G8 CI half).
- **VL-090** - REAL_TRANSPORT green: the attack suite defeated over real cross-host TLS (the gate-1 referent).
- **VL-093 / VL-095** - freshness/stale and B1+B3 defenses proven on real hardware.
- **VL-108** - four-node public surface live under a real CA; author self-test green.
- **VL-109** - white-box review: R-01 + P-01 found and fixed.
- **VL-122** - live publisher-key rotation + byte-anchor->signed correction.
- **VL-128** - live currency sweep: four nodes current; attack suite green version-matched at the deployed commit.

### Corrections, retractions & disputes (the integrity spine)
This is the ledger's real value - the record logs its own errors.
- **VL-004** - an over-strong read retracted.
- **VL-015 -> VL-016** - VL-014 moved SINGLE-SOURCE -> DISPUTED -> CORRECTED.
- **VL-039 follow-up 2** - correction: the envelope is tamper-evident, NOT forgery-resistant (unkeyed hash).
- **VL-043 follow-up 2** - correction: STATE over-claimed a committed artifact that was correctly absent.
- **VL-046** - integrity: an accidental duplicate build entry removed (dedup, not curation).
- **VL-102 / VL-106** - cross-model runs discarded for fabricated citations.
- **VL-109 follow-up 3 (CORRECTION)** - a revert-catcher that did not catch the revert; test fixed, false claim retracted.
- **VL-129** - four public-site overclaims/contradictions corrected ("counsel-finalized" was false).
- **VL-131** - a pre-existing site/index.html truncation repaired.

---

## B. Full chronological index

Every entry, by its own header. Generated from the ledger; do not hand-edit.

- VL-001 - Ledger established
- VL-002 - G0 (CCS specification/implementation drift)
- VL-003 - G1 (README test count) corrected
- VL-004 - "Validator wrapped in oversized language" read retracted
- VL-005 - Grok first review (rating) - NOT a confirmation event
- VL-006 - canon.md transcribed and locked
- VL-007 - v0.9.8.4 known canonical properties (numbering gaps)
- VL-008 - Cross-model verification: task-to-source binding is the operative variable
- VL-009 - ASCII-safe standard applied repo-wide; prior inconsistency corrected
- VL-010 - VL-003 reproducibility restored: MANIFEST/manifest.json committed
- VL-011 - EVIDENCE/ reorganized into proofs/ and archive/; honest-base track complete
- VL-012 - G0 rename + G6 + G10 disambiguation pass; convention decided and applied
- VL-013 - Planning artifacts 05 and 06 brought current to VL-012
- VL-014 - SPEC/request_schema.md drafted; G0 build track started
- VL-015 - Cross-model verification of VL-014: VL-014 -> DISPUTED; G12 + G13 surfaced
- VL-016 - VL-014 corrections applied; premises cross-model-verified; VL-014 -> CORRECTED
- VL-016 follow-up - schema and artifact 04 edits applied; split commit repaired
- VL-017a - Methodology artifacts promoted: verification-request template + apply-script template
- VL-017 - Failing schema-shape tests at PEP boundary (G2 build track, build-order step 2)
- VL-017b - Build-resumption invocation tested against two models; methodology template promoted
- VL-018 - G2 build track: schema validator live build; three VL-017b candidates resolved with rationale; G14 surfaced
- VL-018 follow-up - header convention corrected; docs/methodology/session_mechanics_lessons.md promoted
- VL-019 - PEP wired to validator; G2 closed in code; 27/27 schema tests + 23/23 evaluator regression passing
- VL-019 follow-up - README.md rewritten to reflect current repository state; G1, G3, G4 actions advanced
- VL-020 - artifact 05 freshness pass; methodology Lesson 5 promoted; schema stale forward-reference corrected
- VL-020 follow-up - STATE.md and ledger append; delivery-omission repair
- VL-021 - schema line-457 stale forward-reference correction
- VL-021 follow-up - STATE.md and ledger append; delivery-omission repair
- VL-022 - throwaway-session methodology promotion: cross-model evaluate template and Lesson 6
- VL-023 - 2026-05-20 - Recursive-continuity hypothesis derivation: PARTIAL HOLDS
- VL-023 follow-up - 2026-05-20 - Cross-model evaluation of VL-023 PARTIAL HOLDS verdict
- VL-024 - 2026-05-20 - Strengthening derivation: cross-model run at VL-023 follow-up strengthens recursive-continuity claim on layers B and C
- VL-027 - 2026-05-22 - envelope.py import fix; bug surfaced by planned VL-028 test session
- VL-028 - 2026-05-22 - Canon-derived tests for envelope.py; G7 partial closure for envelope domain
- VL-029 - 2026-05-25 - G0 build half closes: pep.py wires envelope emission + envelope.py ccs-derivation rule + xfail-to-xpass + artifact 04/06 F1 bundle
- VL-029 follow-up - 2026-05-25 - README post-VL-029 staleness corrective (one-off; not a trajectory move)
- VL-030 - 2026-05-26 - T-G3 public framing reframe closes: Zenodo addendum Revision 2 published; repo-internal evidence commit ratifies the substantive work
- VL-031 - 2026-05-26 - T-07 trajectory close: `07_continuity_recursion.md` artifact lands; first pre-draft cross-model verification in project history
- VL-032 - 2026-05-26 - T-methodology trajectory close: methodology backlog from VL-025 through VL-031 absorbed into durable artifacts
- VL-033 - 2026-05-27 - Citation-currency audit: SESSION_PROTOCOL.md citation drift annotated; STATE.md known-items subsection pruned
- VL-034 - 2026-05-28 - Canon-derived tests for the evaluator domain: G7 closes completely
- VL-035 - 2026-05-28 - Methodology refinement: Lessons 2 and 3 sharpened from the VL-033/VL-034 source-first findings
- VL-036 - 2026-05-29 - T-G4-design: non-bypassable enforcement designed; build deferred to VL-037
- VL-037 - 2026-05-29 - T-G4-build: target-side envelope verifier; first G4 build increment (delivery deferred to VL-038)
- VL-037 follow-up - 2026-05-29 - Remove working scratch files committed in a959680; STATE/ledger bookkeeping
- VL-038 - 2026-05-29 - T-G4-enforce: defensible refused bypass; push delivery + enforcing target verifying against the published record
- VL-039 - 2026-05-31 - T-G5-transport: cross-host transport of the published record; trust bootstrapped at one pinned anchor
- VL-039 follow-up - Decision G cross-model evaluate: G5 trust-reduction is PARTIAL; freshness is load-bearing
- VL-039 follow-up 2 - Forgery probe: the envelope is tamper-evident, not forgery-resistant (decision_sha256 is unkeyed)
- VL-040 - 2026-05-31 - T-signing: issuer signing (opt-in); the forgery finding closed on the signed path
- VL-040 follow-up 1 - 2026-05-31 - Signed-path forgery re-probe: convergent NO (construction)
- VL-040 follow-up 2 - 2026-06-02 - Key-governance cross-model evaluate: forgery-resistance is BOUNDED (signed path, uncompromised + authentically-distributed key); key lifecycle is the load-bearing floor
- VL-041 - 2026-06-02 - T-key-lifecycle (expiry): issuer-key validity window (opt-in); undetected-compromise time-bounded
- VL-042 - 2026-06-02 - T-key-record (B-prime-2): published signed key record; revocation built (opt-in); the new publisher/root trust floor
- VL-042 follow-up - 2026-06-02 - New-trust-root cross-model evaluate: forgery-resistance stays BOUNDED; the publisher/root key is the new load-bearing floor (root compromise total, no built recovery)
- VL-043 - 2026-06-02 - T-readiness: the WIRING-track drift gate (the third axis); machine-checked deployment-readiness, fail-closed on dishonesty; 0 of 3 predicates green by design
- VL-043 follow-up 2 - 2026-06-02 - Doc-currency correction: STATE.md over-claimed `EVIDENCE/published_keys.json` as a committed artifact; the absence is correct per artifact 09
- VL-044 - 2026-06-02 - T-root-recovery: planned root rotation + per-root status (B-prime-3); built opt-in, build-then-wire; ROOT_RECOVERY stays RED by design
- VL-044 follow-up - 2026-06-02 - transitive-root-designation cross-model evaluate: SOUND, 3-0 convergent; the forgery-resistant bound does NOT move
- VL-045 - 2026-06-03 - T-prose-drift + T-bookkeeping: doc-freshness, spec-clarification, and methodology catch-up; NO capability or admission-path change
- VL-046 - 2026-06-03 - T-bookkeeping: ledger integrity - the duplicate VL-042 build entry removed
- VL-047 - 2026-06-03 - T-default-secure: the mandatory signing cutover; pep.py's default forward signs; DEFAULT_SECURE goes green (1 of 3)
- VL-048 - 2026-06-03 - T-end-to-end: the signed cross-host chain; END_TO_END_NO_SHORTCUT goes green (2 of 3)
- VL-049 - 2026-06-04 - T-root-recovery-wire: planned root rotation consulted target-side over the signed cross-host chain; ROOT_RECOVERY goes green (3 of 3)
- VL-050 - 2026-06-05 - T-prose-drift + prose-bookkeeping consolidation: narrative refreshed to match the code that outran it; no capability/trajectory advance
- VL-051 - 2026-06-05 - T-server-retire: retire IMPLEMENTATION/server.py
- VL-052 - 2026-06-05 - T-prose-bookkeeping-sweep: the Tier-1 honesty sweep
- VL-053 - 2026-06-06 - T-G11-manifest-source: the manifest-source asymmetry closed via path (b)-with-guard
- VL-054 - 2026-06-06 - T-G14-unknown-key: the unknown-key refusal code resolved via Option A
- VL-055 - 2026-06-06 - T-prose-drift: the G11 prose tail cleared (stale reassert() comment + the three literal-SHA pins)
- VL-056 - 2026-06-06 - T-cross-signer-phrasing: the within-record-vs-cross-signer split verified clean on disk; no spec edit
- VL-057 - 2026-06-06 - T-referent-binding: external-verification-readiness artifact landed; convergence demoted from evidence to framing stress-test
- VL-057 follow-up - 2026-06-06 - the forward teeth landed: Lesson 10 + GR-3
- VL-057 second follow-up - 2026-06-06 - demotion completed: the 5 missed convergence verdicts demoted; two bounding notes
- VL-058 - 2026-06-06 - T-G5-transport: G5 real-transport design artifact (12) + step-1 transport seam (transport.py) built-then-wire; in-env TLS substrate spiked
- VL-058 follow-up - 2026-06-06 - Lesson 11 promoted: Cowork-mount file + git mechanics (the CRLF-from-desktop-tools + unlink-EPERM findings)
- VL-060 - 2026-06-08 - T-G5-transport-wire: the VL-058 transport seam wired onto the default path (pep.py push + published_source.py fetch); byte-identical; step 1b done
- VL-061 - 2026-06-08 - T-G5-transport: artifact 12 step 4 - the standalone, deployable reference enforcing target (supersedes the target.py stub)
- VL-062 - 2026-06-08 - evidence/publication: external-interception evidence committed (webhook.site third-party receiver); Zenodo Enforcement Evidence Addendum advanced to Revision 3
- VL-063 - 2026-06-08 - T-G5-transport: multi-process + real-TLS chain (artifact 12 steps 2-3, in-env); gate / reference target / publisher as three OS processes over CA-verified TLS
- VL-064 - 2026-06-08 - governance / relicense: repository LICENSE changed from MIT to proprietary (all rights reserved); README rights section updated
- VL-065 - 2026-06-08 - T-G5-continuity: decision freshness; A3b sub-case (a) closed - the default ELIGIBLE forward stamps a signed decision max-age and the verifier refuses a stale captured decision
- VL-066 - 2026-06-08 - T-G5-continuity + wedge: replay / exactly-once closed (signed decision_id + executor seen-set); wedge property demonstrated end-to-end on an agent tool-call surface
- VL-067 - 2026-06-08 - directive: road to external readiness (docs/restructure/13) - the ordered local backlog to the external-start line, with a clean code/ledger base
- VL-068 - 2026-06-08 - A1 (artifact 13, Phase A): retire the target.py stub (superseded by the reference enforcing target)
- VL-069 - 2026-06-08 - A2 (artifact 13, Phase A): server.py retirement - NO ACTION (already retired at VL-051); directive + Next-open-action drift corrected
- VL-070 - 2026-06-08 - directive: Cowork sandbox recovery folded into SESSION_PROTOCOL.md (a session boots cleanly without re-deriving it)
- VL-071 - 2026-06-09 - A3 (artifact 13, Phase A): gap-tracker refresh - artifact 04 G4/G5/A3b brought current to VL-061/063/065/066
- VL-072 - 2026-06-09 - A4 (artifact 13, Phase A): STATE.md prose-drift cleared - historical numbered Next-open-action list retired to a provenance pointer; stale gap labels fixed; a pre-existing EOF truncation repaired
- VL-073 - 2026-06-09 - A5 (artifact 13, Phase A): CI wired (.github/workflows/ci.yml) + the g4 runner the gate surfaced repaired
- VL-073 follow-up - 2026-06-09 - A5: the first real CI run made green (g5_multiprocess_tls runner hardened; CI reports all runner failures)
- VL-073 follow-up 2 - 2026-06-09 - A5: de-flake test_manifest_mutation_during_concurrent_evaluation (the second CI run's suite-step failure)
- VL-073 follow-up 3 - 2026-06-09 - A5: green CI reached by excluding the environment-sensitive multi-process-TLS runner from the gate
- VL-073 follow-up 4 - 2026-06-09 - A5: the green CI run recorded; G8 CI-half closed
- VL-059 - 2026-06-09 - A6 (artifact 13, Phase A): deposit-readiness audit recorded; the long-reserved VL-059 slot resolved
- VL-074 - 2026-06-09 - B1 (artifact 13, Phase B): record freshness - the signed published-record reader (A3b sub-case b)
- VL-075 - 2026-06-09 - B2 (artifact 13, Phase B): cross-host clock-skew tolerance on the freshness checks
- VL-076 - 2026-06-09 - B3 (artifact 13, Phase B): shared-replay-cache seam (cross-instance exactly-once)
- VL-077 - 2026-06-09 - B4 (artifact 13, Phase B): real MCP server with the admissibility gate on tool execution
- VL-078 - 2026-06-09 - B5 (artifact 13, Phase B FINAL): latency budget + executor SDK
- VL-079 - 2026-06-09 - C3 (artifact 13, Phase C): attack harness + falsifiable claim sheet (gate-2 scaffolding)
- VL-080 - 2026-06-09 - process/bookkeeping: readiness.json B1-B5 enrollment + artifact-13 EOF-truncation repair
- VL-080 follow-up - 2026-06-09 - CI-red repair: a non-hermetic attack-harness test (local-pass / CI-fail)
- VL-081 - 2026-06-09 - C1 (artifact 13, Phase C): deploy packaging (artifacts authored; container stand-up AUTHOR-locus)
- VL-082 - 2026-06-09 - C2 (artifact 13, Phase C): real TLS/cert + trust bootstrap (artifacts authored; cert material validated, real cross-host TLS AUTHOR)
- VL-083 - 2026-06-09 - C3-live + C4 staging (artifact 13, Phase C): the AUTHOR's real-transport run, made run-it-not-write-it
- VL-084 - 2026-06-09 - prose-drift reconciliation: the narrative docs brought current to the Phase-B/C build (VL-074..VL-083)
- VL-084 follow-up - 2026-06-09 - full-repo audit: one spec-vs-manifest drift found and fixed
- VL-084 follow-up 2 - 2026-06-09 - comprehensive read-every-file audit: four HIGH findings found and fixed
- VL-085 - 2026-06-09 - deploy runbook: Hyper-V two-host provisioning checklist (operational; the author's cross-host stand-up)
- VL-086 - 2026-06-09 - deploy runbook: VirtualBox two-host provisioning checklist (operational; the author's chosen hypervisor)
- VL-087 - 2026-06-09 - C2 cert-tooling bug fix: gen_certs missing SKI/AKI (surfaced by the first live cross-host run)
- VL-088 - 2026-06-09 - attack-harness bug fix: target_url_swap admitted against an unreachable URL (second real-surface finding)
- VL-089 - 2026-06-09 - attack-harness fix: push-delivery positive control (the third, deepest real-surface finding)
- VL-090 - 2026-06-09 - C4 MET: REAL_TRANSPORT green - the attack suite defeated over real cross-host TLS (the gate-1 referent achieved)
- VL-091 - 2026-06-09 - WIRE B1: signed published-record freshness onto the reference target (A3b sub-case (b) closed for a configured deployment)
- VL-092 - 2026-06-09 - deploy-image fix: Dockerfile missing the signed-record generator modules (fourth real-surface finding)
- VL-093 - 2026-06-09 - LIVE: the freshness/stale defense proven on the real surface (the author's TOCTOU attack, defeated cross-host)
- VL-094 - 2026-06-09 - WIRE B3: the shared-replay-cache seam onto the reference target (cross-instance exactly-once reachable)
- VL-095 - 2026-06-09 - LIVE: both wired capabilities (B1 freshness, B3 cross-instance replay) proven on real cross-host hardware
- VL-096 - 2026-06-10 - Three-domain synthetic POC: the unchanged chain characterized across medical / legal / finance
- VL-096 live - 2026-06-10 - Three-domain POC reproduced LIVE over real cross-host TLS (all three domains)
- VL-097 - 2026-06-10 - Envelope inspector / reconciler (local audit tooling; build-then-wire)
- VL-098 - 2026-06-10 - Semantic re-evaluation: the inspector's missing rung (consistency + live re-run of the production evaluator)
- VL-099 - 2026-06-10 - Gate-side issuance log (built AND wired; the reconciler's gate-produced input)
- VL-100 - 2026-06-10 - Cross-model verification of specs 26/27/28 STAGED (request committed; execution is the author's)
- VL-101 - 2026-06-10 - Tooling inventory (docs/TOOLING.md) + README orientation pointer
- VL-102 - 2026-06-10 - VL-100 round adjudicated: specs 26/27/28 CONFIRMED (two clean runs); third run discarded for fabricated citations, its objection refuted on the merits
- VL-103 - 2026-06-10 - External validation execution plan (G5): the operational road from finished in-house work to the only open item
- VL-104 - 2026-06-15 - OPA ext-authz admissibility sidecar built + tested (in-house derivative track; build-then-wire)
- VL-105 - 2026-06-15 - ext-authz sidecar TLS test path: in-sandbox referents (hermetic handshake + real loopback TLS) + the two-VM manual runbook
- VL-106 - 2026-06-15 - OPA sidecar (VL-104/105) claim set cross-model verified: 18/19 conformance CONFIRMED by two clean runs; third run discarded for fabricated citations; CA-9 a named gap; internal conformance only, G5 unchanged
- VL-107 - 2026-06-16 - G5 Phase-1 forks locked + attacker-pack consistency repair (execution session; no code/canon/test change)
- VL-108 - 2026-06-16 - G5 Phase 1 executed: four-node public surface live under a real CA; author self-test green over real transport; REAL_TRANSPORT upgraded from the VirtualBox tier to the public surface
- VL-108 follow-up - 2026-06-16 - pre-exposure items 1-3 executed (publisher key rotated, sidecar claim-13 live-verified, renewal hooks on all nodes)
- VL-109 - 2026-06-16 - Cursor white-box review (Mode A): R-01 + P-01 found & fixed; B-01/F-01/R-02 named-open; in-house hardening, NOT a G5 referent
- VL-109 follow-up - 2026-06-16 - P-01 test hardening: duplicate-envelope DENY tests (sidecar + reference target) after the Mode-A round-2 fix-verification
- VL-109 follow-up 2 - 2026-06-16 - R-01 deterministic revert-catcher + P-01 interaction integration test (round-3 sign-off remediation)
- VL-109 follow-up 3 (CORRECTION) - 2026-06-16 - the follow-up-2 R-01 revert-catcher did not catch the revert; test fixed + false claim retracted
- VL-109 follow-up 4 - 2026-06-16 - Cursor verification-run records committed; STATE suite-count corrected; zero-timing R-01 revert-catcher added
- VL-110 - 2026-06-16 - cross-model white-box round (3 clean runs): R-01/P-01 + crypto core re-confirmed; named-posture gaps; R-02 guard + B-01 scope applied; B-01-step-4/F-01/K-01 scheduled
- VL-110 follow-up - 2026-06-16 - cross-model run outputs committed (referent-binding)
- VL-111 - 2026-06-17 - B-01 build-order step 4 BUILT: sidecar interaction derived from the ext_authz request BODY (in-house half of B-01 closed); build-then-wire, NOT a G5 referent
- VL-112 - 2026-06-17 - F-01 BUILT: optional signed-record (freshness) mode wired into the ext-authz sidecar; build-then-wire, NOT a G5 referent
- VL-113 - 2026-06-17 - T-governance: Feature 1 increment 1a - impact classification (requires_approval) built-then-wire with review fixes H1+H2
- VL-114 - 2026-06-17 - T-governance: Feature 1 increment 1b - the approval grant (approval.py) built-then-wire with review fixes H3/H4/H5/H7
- VL-115 - 2026-06-18 - T-governance: Feature 1 increment 1c - the pep approval WIRING (the first default-path touch + first stateful gate)
- VL-116 - 2026-06-18 - T-governance: Feature 1 increment 1d - the audit half ([FIX H8]) + the approver CLI; Feature 1 mechanism complete
- VL-117 - 2026-06-18 - T-governance: Feature 2 increment 2a - the mTLS client-auth proof (closing A1 at the transport layer)
- VL-118 - 2026-06-18 - T-governance: the integration proof (design 3.3) - Feature 1 and Feature 2 compose
- VL-119 - 2026-06-18 - T-governance: Feature 1 residual R1 - approver provenance + role ([FIX H5] load-bearing half)
- VL-120 - 2026-06-18 - T-governance: Feature 1 residual R2 - shared store for single-use + the pending-set ([FIX H3]/[FIX H4] under horizontal scale)
- VL-121 - 2026-06-18 - T-governance: governance-substrate DEPLOYMENT artifacts authored (operator-locus; R1 + R2 + Feature-2 wiring)
- VL-122 - 2026-06-18 - LIVE-OPS: publisher signing-key ROTATION + byte-anchor->signed correction (VL-108 pre-exposure items 1 & 2 closed)
- VL-123 - 2026-06-18 - T-governance: Cursor white-box review of the governance core - hardening cluster (G-01/03/04/06 FIXED; G-02/05 documented)
- VL-124 - 2026-06-18 - T-governance: cross-model convergence round on the governance core (Cursor + OpenAI + Grok) - VL-123 confirmed; two single-model sharpenings named-open
- VL-125 - 2026-07-01 - T-recruiting: private-invite red-team pack + public one-page site + non-monetary recognition model authored (no code/canon/test/verification change)
- VL-126 - 2026-07-03 - T-bookkeeping close-repair + T-external Phase-3.2 asset: the 40fb5e6 close repaired (pre-launch pack landed, COPYRIGHT_HEADER retired, session-local files ignored) + the rebuild-estimator commissioning brief authored
- VL-127 - 2026-07-03 - T-recruiting: channel re-alignment - no bug-bounty platform; the site disclaimer + LinkedIn posts are the solicitation channels; residual platform/cash references purged; LinkedIn drafts authored
- VL-128 - 2026-07-03 - LIVE currency sweep: all four public nodes verified current; live attack suite green version-matched at 3343e32 (author self-test, NOT external validation)
- VL-129 - 2026-07-03 - SITE honest-scope cleanup: four public-site overclaims/contradictions corrected in the repo-canonical site/index.html; live WordPress copy still to update
- VL-130 - 2026-07-03 - T-recruiting: G5 conversion kit - seven paste-ready assets to convert public solicitation into an engaged blind external red-teamer
- VL-131 - 2026-07-03 - SITE build-out of the conversion kit + repair of a pre-existing site/index.html truncation
