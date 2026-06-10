# Elyon-Sol POC — Finance — order/trade execution

_Mode: **live** · cases: 13 · passed: 12/13 · generated 2026-06-10 20:48:45Z_

> **Synthetic data.** All identifiers (patient/account/matter/bar/NPI numbers, URLs) are fictional and resolve to nothing real. This is a characterization run of the production admission chain (GR-3), not an external validation.

## Policy manifest (what this domain requires to admit)

- **version**: `fin-1.0`
- **manifest sha256**: `7750509396e8aa8747cc06a7e1ed6af3d79f83ae54cbe30fe7f4e75c127b7c40`
- **required authority set (AR)** — the caller's authorities must cover this: `trader_identity, desk_authorization, limit_check_cleared`
- **required operation set (R)** — the operation must cover this: `trade:execute`

A call is **admitted** only if its authority set ⊇ AR (AC³), its operation set ⊇ R (T²⁶), and it is pinned to this exact manifest version+sha (manifest-integrity); otherwise the gate **refuses**. An admitted call carries a signed envelope the executor re-checks (signature → currency → binding → freshness → replay) before acting.

## Cases

### admit_primary — ✅ PASS

_A desk-authorized trader executes BUY 1,000 AAPL within limits — admitted and executed._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `f336bd894b864373aa3baca6e1f7fe71`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:44.845319+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `daabec6ed82ad5b4…`
  - decision_sha256: `f99e7ab96e9218d1…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_secondary — ✅ PASS

_The same trader executes SELL 500 MSFT — admitted and executed._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: MSFT; side: SELL; quantity: 500; notional_usd: 210000; desk: equities-cash; trader_id: TRD-441; order_sha256: c261e2fa4e7840dd…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `bda15abbb97a4019b98aa19d76474ee6`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:44.947843+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `c1517f65ba403d80…`
  - decision_sha256: `13b9d27669d5fddb…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_minimal_authority — ✅ PASS

_Exactly the required clearances, no extras — still admissible._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `a55d88f0016b412dae51f48a5d2cd1c9`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:45.016074+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `53191c56d8cb3984…`
  - decision_sha256: `db5fa07d59692508…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### insufficient_authority — ✅ PASS

_A trade that failed the pre-trade limit check is not admissible._

- **actor (AP)**: `trader_identity, desk_authorization, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### wrong_operation — ✅ PASS

_A quote request is not an execution and is refused._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:quote`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### stale_policy_pin — ✅ PASS

_A trade pinned to a superseded risk-policy version is refused._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: REFUSE — AC3, T26, MANIFEST_INTEGRITY unsatisfied
  - AC³=False · T²⁶=False · manifest-integrity=False
- **executor**: not reached (refused at the gate)

### unattested — ✅ PASS

_An execution reaching the OMS with no attestation is refused._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: (no envelope — A1 / un-attested path)
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_ENVELOPE_ABSENT`)
- **expected**: refused (`REF_VERIFY_ENVELOPE_ABSENT`)

### forged_envelope — ✅ PASS

_An attacker who edits the size inside the attestation is caught by the signature._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `e8729af70129464a889fe09aa5d22c6c`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:45.134479+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `cee259f72a0ead32…`
  - decision_sha256: `f99e7ab96e9218d1…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_INVALID`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_INVALID`)

### replay — ✅ PASS

_A single execution authorization cannot be used to execute the trade twice._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `d9ef7f1a5323407ba80b6cdfe8fdd71e`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:45.192556+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `490c974007f02d6f…`
  - decision_sha256: `f99e7ab96e9218d1…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_REPLAY`)
- **expected**: refused (`REF_VERIFY_REPLAY`)

### rebind_operation — ✅ PASS

_An execute authorization cannot be repurposed to cancel an order._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:cancel`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `b3197b1a44a04ed5862c8584f8377ff9`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:45.274276+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `2bd16875c8095138…`
  - decision_sha256: `f99e7ab96e9218d1…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### rebind_context — ✅ PASS

_The size cannot be inflated to 100,000 after the limit check passed._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 100000; notional_usd: 19500000; desk: equities-cash; trader_id: TRD-441; order_sha256: eb5b025fd87b1b14…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `3e418a5217fa4bbc94b34e28fa2a2300`
  - bound target_url: `https://192.168.56.102:9000/target`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:45.333353+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `e9b1c711383ed656…`
  - decision_sha256: `f99e7ab96e9218d1…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### target_swap — ✅ PASS

_An OMS authorization cannot be redirected to the settlement-instruction endpoint._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `5193950b4c0d4e24b24ef58872462378`
  - bound target_url: `https://192.168.56.102:9000/target-SWAP`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T20:53:45.391710+00:00`
  - issuer_key_id: `gate-deploy-001` · signature: `09f9260a041f1fff…`
  - decision_sha256: `cb644f981f5a07dc…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### stale_decision — ❌ FAIL

_An expired authorization is not honored._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: (no envelope — A1 / un-attested path)
- **executor verdict**: REFUSED — not acted (`SKIPPED (pass --decision-max-age to match the gate window)`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_EXPIRED`)

