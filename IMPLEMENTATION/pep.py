"""
Elyon-Sol Policy Enforcement Point (PEP).

This module is the HTTP boundary of the gate. It performs schema
validation BEFORE evaluation, evaluation BEFORE upstream forwarding,
and fail-closed on any exception. Schema validation order is
load-bearing per SPEC/request_schema.md "PEP boundary behavior."

Wired in VL-019 to close G2 in code. Prior to VL-019, this module
accepted a flat `{target_url, context}` body via a Pydantic model
and performed no schema validation; the wire shape changed to
`{target_url, interaction}` per SPEC/request_schema.md and the
validator from IMPLEMENTATION/request_validator.py (VL-018) is
called before evaluate(). The endpoint reads the raw JSON body
(no Pydantic body model) so that the validator can inspect the
full set of top-level keys; a Pydantic model with fixed fields
would silently drop extra top-level keys (like `AP`, `OP`, or
`ccs_valid` alongside a valid `interaction`), mapping
spec-distinguished refusals (REF_SCHEMA_FLAT_KEYS,
REF_SCHEMA_RESERVED_CCS) onto a generic REF_SCHEMA_TOP_LEVEL.

Refusal payloads at the schema layer use the seven-code vocabulary
named in SPEC/request_schema.md "PEP boundary behavior" and exported
from IMPLEMENTATION/request_validator.py:
  REF_SCHEMA_PARSE_ERROR              (emitted here by the
                                       JSON-decode catch)
  REF_SCHEMA_TOP_LEVEL                (emitted by the validator)
  REF_SCHEMA_BAD_URL                  (emitted by the validator)
  REF_SCHEMA_FLAT_KEYS                (emitted by the validator)
  REF_SCHEMA_MANIFEST_PINNING_MISSING (emitted by the validator)
  REF_SCHEMA_RESERVED_CCS             (emitted by the validator)
  REF_SCHEMA_TYPE_MISMATCH            (emitted by the validator)

REF_SCHEMA_TOP_LEVEL is emitted directly by the validator (see
request_validator.py lines 308 and 337-342); the PEP does not
import it because it does not emit it. The PARSE_ERROR import is
the only schema-vocabulary constant used at this boundary.

Extended in VL-029 to emit admissibility envelopes on ELIGIBLE per
docs/restructure/05_admissibility_envelope_spec.md build-order step 5.
On ELIGIBLE, the PEP calls safe_manifest + the three condition
functions (ac3_valid, t26_valid, manifest_integrity_valid) per
Decision C1, then calls build_envelope() to construct the envelope,
then attaches the envelope to the response payload per Decision E
({"decision": "ELIGIBLE", "envelope": <envelope>}). REFUSE response
shape is unchanged from VL-019; envelope-on-REFUSE is build-outward
scope per artifact 05 open question 3 (G4 territory).

VL-047 mandatory signing cutover: the ELIGIBLE branch now SIGNS the
envelope (sign_envelope) before pushing and returning it, using a signing
key from a runtime source (_get_signing_key; an env var or an injected key
object, never the repo). A gate with no configured key FAILS CLOSED
(REF_PEP_FAIL_CLOSED via the envelope-construction try/except), never a
downgrade to an unsigned forward. verify_envelope's unsigned mode is
unaffected (it remains for target-side enforcement and A1-bypass
demonstrations). DEFAULT_SECURE goes green (EVIDENCE/readiness.json).
"""

import json
import os

import requests
from fastapi import FastAPI, HTTPException, Request

from IMPLEMENTATION.evaluator import (
    load_manifest,
    evaluate,
    safe_manifest,
    ac3_valid,
    t26_valid,
    manifest_integrity_valid,
)
from IMPLEMENTATION.envelope import build_envelope, canonical_json, sign_envelope
from IMPLEMENTATION.request_validator import (
    validate_request,
    REF_SCHEMA_PARSE_ERROR,
)
from IMPLEMENTATION.transport import post_to_target


app = FastAPI(title="Elyon-Sol PEP")


# VL-047 mandatory signing cutover: the gate's default forward signs every
# emitted envelope, so the gate now needs a signing PRIVATE key at runtime.
# Custody (artifact 09 / artifact 05 "Key model"): the private key is NEVER in
# the repository. _get_signing_key() resolves, in order, a process-injected key
# object (a test harness or a deployment shim) then the ELYON_SIGNING_KEY_HEX +
# ELYON_SIGNING_KEY_ID environment pair. It returns (signing_key, key_id) or
# None; None makes the ELIGIBLE branch fail closed (REF_PEP_FAIL_CLOSED), never
# a downgrade to an unsigned forward. cryptography is imported lazily inside the
# function so this module stays import-clean (matching envelope/verifier
# duck-typing); the injected object need only expose .sign(bytes) -> bytes.
_INJECTED_SIGNING_KEY = None  # set to (signing_key, key_id) by a harness/deploy


def _get_signing_key():
    if _INJECTED_SIGNING_KEY is not None:
        return _INJECTED_SIGNING_KEY
    key_hex = os.environ.get("ELYON_SIGNING_KEY_HEX")
    key_id = os.environ.get("ELYON_SIGNING_KEY_ID")
    if key_hex and key_id:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )
        return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex)), key_id
    return None


def _schema_refusal_exception(code: str) -> HTTPException:
    """
    Build the standard schema-layer refusal HTTPException. Status
    403 with detail payload {"terminal_state": "REFUSE",
    "refusal_reason_code": <code>} per the assertions in
    TESTS/adversarial/test_request_schema.py.
    """
    return HTTPException(
        status_code=403,
        detail={
            "terminal_state": "REFUSE",
            "refusal_reason_code": code,
        },
    )


@app.post("/governed-call")
async def governed_call(request: Request):
    """
    Boundary behavior order per SPEC/request_schema.md
    "PEP boundary behavior":

      1. Parse JSON. Failure -> REFUSE with REF_SCHEMA_PARSE_ERROR.
      2-5. Schema validation via validate_request(). Failure ->
         REFUSE with the validator-emitted code (REF_SCHEMA_TOP_LEVEL,
         REF_SCHEMA_BAD_URL, REF_SCHEMA_FLAT_KEYS,
         REF_SCHEMA_MANIFEST_PINNING_MISSING, REF_SCHEMA_RESERVED_CCS,
         or REF_SCHEMA_TYPE_MISMATCH).
      6. evaluate() on the validator's normalized interaction. REFUSE
         -> HTTPException(403, terminal_state=REFUSE). ELIGIBLE ->
         construct envelope (Decision C1: ac3/t26/manifest_integrity
         derived via the three condition functions on safe_manifest;
         build_envelope() per artifact 05 build-order step 5), sign it
         (VL-047 cutover; fail-closed if no key is configured), then
         forward to target_url, then return
         {"decision": "ELIGIBLE", "envelope": <envelope>} per
         Decision E.

    The endpoint reads the request body as raw bytes rather than
    binding to a Pydantic model because the validator owns
    full-body inspection: the spec's flat-key check
    (REF_SCHEMA_FLAT_KEYS) and the spec's top-level CCS check
    (REF_SCHEMA_RESERVED_CCS for keys like `ccs_valid` alongside
    a valid `interaction`) both require visibility of the original
    top-level keys. Pydantic projection to a fixed model
    (`{target_url, interaction}`) would silently drop the very keys
    the validator must refuse, mapping spec-distinguished refusals
    onto a single REF_SCHEMA_TOP_LEVEL diagnosis. Pydantic's role
    here would be redundant with the validator's own type checks;
    omitting it preserves the seven-code vocabulary discrimination
    the test suite requires.

    Schema-layer refusals do not call evaluate() and do not call
    requests.post; the function returns through HTTPException
    before reaching either. Evaluator-layer refusals do not call
    requests.post.

    The fail-closed exception catch wraps evaluate() and the
    upstream call only. Schema-layer parse and validation errors
    raise HTTPException directly; they do not flow through the
    catch.
    """
    # ----- Step 1: Parse JSON -----
    raw = await request.body()
    try:
        body = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        raise _schema_refusal_exception(REF_SCHEMA_PARSE_ERROR)

    # ----- Steps 2-5: Schema validation -----
    normalized_interaction, refusal = validate_request(body)
    if refusal is not None:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": refusal,
            },
        )

    # ----- Evaluation -----
    try:
        manifest = load_manifest()
        result = evaluate(normalized_interaction, manifest)
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    if result != "ELIGIBLE":
        # Evaluator-layer REFUSE. Refusal payload preserved from
        # pre-VL-019 pep.py: {"terminal_state": "REFUSE"} without a
        # refusal_reason_code, because VL-019's scope is schema-layer
        # wiring and the evaluator-layer refusal vocabulary is not
        # specified by SPEC/request_schema.md. Introducing an
        # REF_EVAL_* code here would be vocabulary not derived from
        # the spec this commit cites.
        raise HTTPException(
            status_code=403,
            detail={"terminal_state": "REFUSE"},
        )

    # ----- Envelope construction (G0 build half close at VL-029) -----
    # Canonical CCS per artifact 05 + canon section 12. Decision C1:
    # condition booleans derived independently in pep.py rather than
    # from evaluator.evaluate()'s aggregate return. safe_manifest()
    # is re-called here (it already succeeded inside evaluate()) so
    # the envelope construction is locally self-consistent: each
    # boolean passed to build_envelope has a direct visible derivation
    # in pep.py. Wrapped in try/except (W2 fail-closed discipline):
    # an unexpected exception in any condition function or in
    # build_envelope() must raise REF_PEP_FAIL_CLOSED, matching the
    # symmetric protection around evaluate() and the upstream POST.
    try:
        safe_mfst = safe_manifest(manifest)
        ac3 = ac3_valid(normalized_interaction, safe_mfst["AR"])
        t26 = t26_valid(normalized_interaction, safe_mfst["R"])
        mi = manifest_integrity_valid(normalized_interaction, safe_mfst)
        envelope = build_envelope(
            decision="ELIGIBLE",
            target_url=body["target_url"],
            normalized_interaction=normalized_interaction,
            manifest=safe_mfst,
            ac3=ac3,
            t26=t26,
            manifest_integrity=mi,
        )
        # VL-047 mandatory signing cutover: sign the envelope on the default
        # forward. The signed object is used for BOTH the push header and the
        # response. No signing key -> fail closed here (caught below as
        # REF_PEP_FAIL_CLOSED), never a downgrade to an unsigned forward.
        signing = _get_signing_key()
        if signing is None:
            raise RuntimeError(
                "no signing key configured; gate fails closed rather than "
                "forward unsigned (VL-047 mandatory signing cutover)"
            )
        signing_key, key_id = signing
        envelope = sign_envelope(envelope, signing_key, key_id)
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    # ----- Upstream forwarding (ELIGIBLE) -----
    # VL-038 push delivery (artifact 08 section 4.3 push variant). The
    # envelope rides as an out-of-band attestation header so the
    # forwarded body stays byte-identical to a direct (un-routed) call;
    # an enforcing target keys on the header's presence and validity
    # (verify_envelope + published-record check), not on the body. Body
    # is unchanged (normalized_interaction). canonical_json gives an
    # ASCII (ensure_ascii=True) string, so the header value is
    # transport-safe. Push deepens the pre-existing canon section 14
    # tension (the gate does more on the execution hop); caller-carry is
    # the section-14-faithful later architecture (artifact 08 sections
    # 4.3 / 5; recorded in artifact 04 G4 + artifact 06 section 14).
    try:
        upstream = post_to_target(
            body["target_url"],
            normalized_interaction,
            {"X-Elyon-Sol-Envelope": canonical_json(envelope)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e),
            },
        )

    return {
        "decision": "ELIGIBLE",
        "envelope": envelope,
    }
