# Governance-Layer Build — Session Kickoff

**How to use:** run this in a NATIVE environment (Claude Code in your terminal on the
laptop, or hand-applied edits) — NOT a fresh Cowork session. The build must touch the real
filesystem with native git; the Cowork sandbox mount truncates files on read, and you must
never edit source you can't reliably read. Paste the "Opener" block below as the first
message; it is self-sufficient and needs no memory of the prior conversation.

---

## Files this session must read (in order)

1. `docs/SESSION_PROTOCOL.md` — grounds off STATE.md + the ledger.
2. `STATE.md` — current project state / next open action.
3. `EVIDENCE/verification_ledger.md` — current VL position, canon lock, open items.
4. `docs/design/governance_layer_design.md` — the full spec for this work.

---

## Opener (paste as the first message)

```
Repo: ~/Elyon-Sol (connect it / run this natively — the build must be on the real
filesystem with native git; do NOT edit source through a truncating mount).

1. Run docs/SESSION_PROTOCOL.md to ground off STATE.md + EVIDENCE/verification_ledger.md
   (this tells you canon version, current HEAD/VL, and open items).
2. Read docs/design/governance_layer_design.md in full — that is the spec for this work.
3. Build Feature 1 (human oversight / PENDING_APPROVAL) FIRST, per §5:
   - keep evaluator.evaluate() two-valued; do NOT modify CANON (new states layer above G(I));
   - add HIGH_IMPACT to MANIFEST/manifest.json + requires_approval() (manifest-derived,
     never caller-supplied);
   - add IMPLEMENTATION/approval.py reusing envelope.py's Ed25519 + binding primitives;
   - insert the approval branch in pep.governed_call (202 PENDING_APPROVAL; approved
     resubmit forwards; bad grant -> REF_APPROVAL_*);
   - enforce separation of duties (approver_key_id != gate_key_id), action-binding,
     freshness, single-use via replay_cache;
   - write the §1.8 tests INCLUDING the revert-catchers, and prove each goes RED on revert
     before trusting it (especially: high-impact-without-grant must never reach requests.post).
4. Record one VL entry for the increment. Canon stays locked. Do not claim the oversight
   guarantee until Feature 2 (non-bypassable) is deployed.
5. Then build Feature 2 (non-bypassable) and the integration proof per §2 and §3.

Maintain radical-honesty / anti-overclaim discipline throughout. White-box / cross-model
results are NOT external validation and never enter the attacker pack.
```

---

## Carry-across flags (so the new session doesn't trip)

- **Canon is locked at v0.9.8.4** and this build does NOT change it — `PENDING_APPROVAL` and
  the external-grant states layer ABOVE `G(I)` (precedent: `reassert()` outcomes). A
  canonical third state is a separate canon-version event, out of scope here.
- The **publisher-key regeneration** and **counsel safe-harbor** gates (TLS dossier §9) are
  about EXTERNAL EXPOSURE, not this build. They don't block coding; don't conflate "feature
  built" with "ready to expose."
- **Build order dependency:** Feature 2 (non-bypassable) is the prerequisite for Feature 1's
  *guarantee*, but Feature 1's *mechanism* is testable in isolation — which is why it's first.
