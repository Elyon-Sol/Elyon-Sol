# Elyon-Sol

Pre-execution governance substrate.

Determines whether an interaction is **eligible to exist** before execution.

---

## Run (PEP Interception Layer v0.9.8.4)

```bash
python -m uvicorn IMPLEMENTATION.pep:app --reload
```

Server:

```
http://127.0.0.1:8000
```

---

## Endpoint

```
POST /governed-call
```

---

## Request Format

```json
{
  "target_url": "https://example.com/api",
  "context": {
    "AP": ["identity", "role"],
    "OP": ["session", "request"],
    "ccs_valid": true
  }
}
```

---

## Behavior

- Evaluator returns `ELIGIBLE` or `REFUSE`
- `REFUSE` → HTTP 403 (upstream not called)
- `ELIGIBLE` → request forwarded to `target_url`

---

## Example (REFUSE)

```bash
curl -X POST http://localhost:8000/governed-call \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://httpbin.org/post",
    "context": {
      "AP": [],
      "OP": [],
      "ccs_valid": false
    }
  }'
```

---

## Example (ELIGIBLE)

```bash
curl -X POST http://localhost:8000/governed-call \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://httpbin.org/post",
    "context": {
      "AP": ["identity", "role"],
      "OP": ["session", "request"],
      "ccs_valid": true
    }
  }'
```

---

## Tests

```bash
python -m pytest TESTS/test_pep.py -v
```

Expected:

```
3 passed
```

---

## Guarantees

- Fail-closed enforcement  
- No retries  
- No fallback execution  
- Deterministic gating via evaluator  

---

## Repository Structure

```
CANON/
IMPLEMENTATION/
MANIFEST/
TESTS/
```

---

## Status

- Canon: v0.9.8.4 (locked)
- Phase: Implementation
- Mode: Deterministic enforcement only
