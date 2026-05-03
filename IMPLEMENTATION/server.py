from fastapi import FastAPI, Request, HTTPException
import requests
import json

from IMPLEMENTATION.evaluator import evaluate, load_manifest

app = FastAPI()


@app.post("/governed-call")
async def governed_call(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=403, detail="REFUSE")

    manifest = load_manifest()

    decision = evaluate(body, manifest)

    if decision != "ELIGIBLE":
        raise HTTPException(status_code=403, detail="REFUSE")

    target_url = body.get("target_url")

    if not target_url:
        raise HTTPException(status_code=403, detail="REFUSE")

    try:
        resp = requests.post(target_url, json=body.get("payload", {}))
        return {"status": "FORWARDED", "response": resp.text}
    except Exception:
        raise HTTPException(status_code=403, detail="REFUSE")
