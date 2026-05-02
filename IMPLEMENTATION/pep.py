import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from IMPLEMENTATION.evaluator import load_manifest, evaluate

app = FastAPI(title="Elyon-Sol PEP")

class GovernedCallRequest(BaseModel):
    target_url: str
    context: Dict[str, Any]


@app.post("/governed-call")
def governed_call(req: GovernedCallRequest):
    try:
        manifest = load_manifest()
        result = evaluate(req.context, manifest)

        if result != "ELIGIBLE":
            raise HTTPException(
                status_code=403,
                detail={
                    "terminal_state": "REFUSE"
                }
            )

        upstream = requests.post(
            req.target_url,
            json=req.context,
            timeout=10
        )

        return {
            "terminal_state": "ELIGIBLE",
            "upstream_status": upstream.status_code,
            "upstream_response": upstream.text
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail={
                "terminal_state": "REFUSE",
                "refusal_reason_code": "REF_PEP_FAIL_CLOSED",
                "error": str(e)
            }
        )
