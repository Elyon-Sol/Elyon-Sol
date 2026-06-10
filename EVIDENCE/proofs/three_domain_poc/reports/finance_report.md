# Elyon-Sol POC — Finance — order/trade execution

_Mode: **inproc** · cases: 13 · passed: 13/13 · generated 2026-06-10 19:47:07Z_

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
  - decision_id: `721e50bee651477985872e00254bf373`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.453962+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `704bef8231d67304…`
  - decision_sha256: `f53164dcd3ea819e…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_secondary — ✅ PASS

_The same trader executes SELL 500 MSFT — admitted and executed._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: MSFT; side: SELL; quantity: 500; notional_usd: 210000; desk: equities-cash; trader_id: TRD-441; order_sha256: c261e2fa4e7840dd…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `11a9a10d8b794c4885ca86dfdcfa098e`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.464630+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `8b176ab824eaa6ba…`
  - decision_sha256: `c0247d04c9abfafa…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### admit_minimal_authority — ✅ PASS

_Exactly the required clearances, no extras — still admissible._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `5719b8ff595c4f088a29cf8c7ace2e2f`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.474884+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `353fda6a978c957d…`
  - decision_sha256: `cd28c7e82ba0d130…`
- **executor verdict**: HONORED — acted (`REASSERTED_AND_BOUND`)
- **expected**: honored (`REASSERTED_AND_BOUND`)

### insufficient_authority — ✅ PASS

_A trade that failed the pre-trade limit check is not admissible._

- **actor (AP)**: `trader_identity, desk_authorization, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: REFUSE — AC3 unsatisfied
  - AC³=False · T²⁶=True · manifest-integrity=True
- **executor**: not reached (refused at the gate)

### wrong_operation — ✅ PASS

_A quote request is not an execution and is refused._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:quote`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: REFUSE — T26 unsatisfied
  - AC³=True · T²⁶=False · manifest-integrity=True
- **executor**: not reached (refused at the gate)

### stale_policy_pin — ✅ PASS

_A trade pinned to a superseded risk-policy version is refused._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: REFUSE — MANIFEST_INTEGRITY unsatisfied
  - AC³=True · T²⁶=True · manifest-integrity=False
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
  - decision_id: `ebb70d81a1f84656a65d81a26a706859`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.499784+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `8ddbc243d9657cda…`
  - decision_sha256: `f53164dcd3ea819e…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_INVALID`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_INVALID`)

### replay — ✅ PASS

_A single execution authorization cannot be used to execute the trade twice._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `86825662cd9c4cabb37686737db5be49`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.508133+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `0212aa165bb7354a…`
  - decision_sha256: `f53164dcd3ea819e…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_REPLAY`)
- **expected**: refused (`REF_VERIFY_REPLAY`)

### rebind_operation — ✅ PASS

_An execute authorization cannot be repurposed to cancel an order._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:cancel`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `e6b05ccd6b614d4c96e1f35318d5d300`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.519892+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `c79ab17397186dad…`
  - decision_sha256: `f53164dcd3ea819e…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### rebind_context — ✅ PASS

_The size cannot be inflated to 100,000 after the limit check passed._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 100000; notional_usd: 19500000; desk: equities-cash; trader_id: TRD-441; order_sha256: eb5b025fd87b1b14…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `f09a376ef6bf4a3d8616e9a5ca9c46a4`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.530497+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `fe326acc2d95a145…`
  - decision_sha256: `f53164dcd3ea819e…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### target_swap — ✅ PASS

_An OMS authorization cannot be redirected to the settlement-instruction endpoint._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `ca90ebcde48a469f8d6abccf512b655c`
  - bound target_url: `https://settlement.bank.example/instruct`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:52:07.541493+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `73155c53f6ac0f12…`
  - decision_sha256: `52c08775fd205550…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_BINDING_MISMATCH`)
- **expected**: refused (`REF_VERIFY_BINDING_MISMATCH`)

### stale_decision — ✅ PASS

_An expired authorization is not honored._

- **actor (AP)**: `trader_identity, desk_authorization, limit_check_cleared, compliance_attestation`
- **operation (OP)**: `trade:execute`
- **trade order (context)**: account: ACCT-55012; instrument: AAPL; side: BUY; quantity: 1000; notional_usd: 195000; desk: equities-cash; trader_id: TRD-441; order_sha256: b7d4b2ecacb63c19…
- **gate decision**: ELIGIBLE — signed envelope issued
  - decision_id: `5b70c0ec562642899258b15e0097fe1b`
  - bound target_url: `https://oms.bank.example/orders/execute`
  - manifest pin: `fin-1.0` / `7750509396e8…`
  - not_after: `2026-06-10T19:47:08.551007+00:00`
  - issuer_key_id: `poc-gate-key-001` · signature: `d778db944cc53c41…`
  - decision_sha256: `f53164dcd3ea819e…`
- **executor verdict**: REFUSED — not acted (`REF_VERIFY_SIGNATURE_EXPIRED`)
- **expected**: refused (`REF_VERIFY_SIGNATURE_EXPIRED`)

