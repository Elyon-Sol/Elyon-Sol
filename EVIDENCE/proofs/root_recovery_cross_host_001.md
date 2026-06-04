# root_recovery_cross_host_001 -- proof of record (VL-049, T-root-recovery-wire)

The no-shortcut proof for the **ROOT_RECOVERY** deployment predicate
(`docs/restructure/10_readiness_spec.md` section 4 item 3). Runner:
`EVIDENCE/proofs/root_recovery_cross_host_001_runner.py`. Run from repo root:

```
PYTHONPATH=. python3 EVIDENCE/proofs/root_recovery_cross_host_001_runner.py
```

Exits 0 iff all invariants hold. The captured run output is
`root_recovery_cross_host_001_runner.log` (authoritative from the real env).

## What it proves

It extends the VL-048 signed cross-host chain
(`g5_signed_cross_host_001_runner.py`) with the VL-044 planned-rotation +
per-root-status mechanism, run over real transport with no test-only shortcut:

```
caller -> gate (signs on the DEFAULT path via the PRODUCTION env-var key path)
       -> push (X-Elyon-Sol-Envelope header)
       -> TRANSPORT (real loopback sockets; production fetch_published_record
          + fetch_root_record + fetch_key_record)
       -> target (separate process, genuinely divergent disk; pins ONLY R1
          out-of-band and never re-pins) -> honor / refuse
```

The target, pinning only R1, fetches the root record (R1 designates R2), builds
the status view, fetches the key record (signed by the designated-active R2,
vouching the gate's issuer key), validates it against the status view via the
VL-049 `fetch_key_record(..., root_status_view=...)` passthrough, then verifies
the envelope's signature against the R2-vouched key, currency against the fetched
published record, and binding.

## Killer property

A target pinning **only R1**, never re-pinned, on a **divergent disk**, HONORS a
gate-signed envelope whose issuer key is vouched by a key record signed by the
**designated-active successor R2** -- a planned in-band R1->R2 rotation with no
re-pin -- while the local-disk contrast (no `record_source`) would have refused
with `REF_VERIFY_REASSERT_RE_EVALUATE_REQUIRED`.

## Cases

| # | case | honored | reason |
|---|------|---------|--------|
| 1 | KILLER: signed valid; R1 designates R2; key vouched by R2 (divergent disk) | True | `REASSERTED_AND_BOUND` |
| 2 | keyless forge (no signature); R2-vouched key | False | `REF_VERIFY_SIGNATURE_INVALID` |
| 3 | revoked R2 signs the key record | False | `REF_VERIFY_ROOT_REVOKED` |
| 4 | retired R2 signs a NEW key record | False | `REF_VERIFY_ROOT_RETIRED` |
| 5 | root-record fetch failure (dead socket) | False | `REF_VERIFY_ROOT_RECORD_INVALID` |
| 6 | stale root record (now >= not_after) | False | `REF_VERIFY_ROOT_RECORD_STALE` |

## No-shortcut (the four forbidden shortcuts of section 4.2, each avoided)

- **Not a hand-built envelope** -- produced by the real `pep.py` /governed-call
  path, signed by `pep._get_signing_key`.
- **Not in-process key injection** -- the gate resolves its signing key through
  the production `ELYON_SIGNING_KEY_HEX` + `ELYON_SIGNING_KEY_ID` pair; the
  autouse conftest fixture is not used (this is not a pytest test).
- **Not a loopback stub** -- the published, root, and key records each cross a
  real `http.server` socket via the production `fetch_*` functions; nothing on
  the fetch boundary is monkeypatched.
- **Not a target importing gate internals** -- the target is a subprocess on a
  byte-mutated `evaluator.py` (genuinely divergent disk); it imports only the
  verifier + the three readers + envelope key reconstruction, holds R1's public
  key as out-of-band configuration, and never imports `pep.py`.

## Decisions (carried)

- **Reading (A)** (Checkpoint A): ROOT_RECOVERY is target-side rotation over the
  VL-048 transport; the gate default forward is unchanged. `wired_to_default`
  stays false honestly; green is `exercised_e2e` + `transported` (mirrors
  END_TO_END).
- **Option (b)** (Checkpoint C): an additive `root_status_view=None` passthrough
  on `fetch_key_record` (threaded to the unchanged `load_key_record_from_bytes`)
  is the only seam by which the production transport wrapper validates a fetched
  key record against a root-status view. Default None = VL-042 byte-behavior.
- **Option alpha**: the pytest ANCHOR (`test_root_recovery_wired`) is the
  in-process logic regression gate; the runner owns the no-shortcut transport.

## Honest bounds

Greening ROOT_RECOVERY means a planned in-band R1->R2 rotation is consulted
target-side over real transport with no shortcut, and revoked/retired roots fail
closed. It does **not** close root-key **compromise** recovery (irreducibly
out-of-band; artifact 11 section 2, the named non-goal). It does **not** assert
true multi-machine + TLS (the named **G5** floor; deployment). "3 of 3 green" is
the finite road walked, **not** "deployed" or "secure". "forgery-resistant"
stays bounded (signed-path-under-uncompromised-root) and out of any deposit.

Ledger: VL-049 (T-root-recovery-wire; ROOT_RECOVERY green, 3 of 3). Spec 52d3764.
