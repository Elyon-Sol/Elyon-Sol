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
"""

import json

import requests
from fastapi import FastAPI, HTTPException, Request

from IMPLEMENTATION.evaluator import load_manifest, evaluate
from IMPLEMENTATION.request_validator import (
    validate_request,
    REF_SCHEMA_PARSE_ERROR,
)


app = FastAPI(title="Elyon-Sol PEP")


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
         forward to target_url.

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

    # ----- Upstream forwarding (ELIGIBLE) -----
    try:
        upstream = requests.post(
            body["target_url"],
            json=normalized_interaction,
            timeout=10,
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
        "terminal_state": "ELIGIBLE",
        "upstream_status": upstream.status_code,
        "upstream_response": upstream.text,
    }
