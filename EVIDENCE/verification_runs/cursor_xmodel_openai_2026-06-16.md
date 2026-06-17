WHITE-BOX cross-model run | model=OpenAI | 2026-06-16 | internal evidence, NOT external validation (VL-057), NOT a G5 referent. Verbatim Cursor output, ASCII-normalized (VL-009).

Verdict: BREAK FOUND. R-01: SOUND. P-01: SOUND.

Findings
id | class | file:line | invariant violated | trigger | severity | repro/PoC | suggested fix
F-01 | binding / sidecar fail-open relative to live request | authz_sidecar.py:194-220, 280-312, 323-328 | Sidecar ALLOW is not bound to the actual authorized HTTP request; it is bound to caller-supplied X-Elyon-Sol-Interaction plus configured target id. | Present a valid signed envelope for benign interaction X and set X-Elyon-Sol-Interaction to X, while the actual request path/body being authorized is Y. | High | /authz/{rest:path} accepts any suffix and "decision reads only headers, never the path" at 323-328; extractor reads interaction solely from header at 194-220; gate checks that header-derived interaction at 300-312. | Derive the live interaction inside the sidecar from the ext_authz request attributes/body/method/path, or cryptographically bind the forwarded request bytes/path/method to the envelope. Do not trust a client-controlled interaction header as the live request.

Probed-and-held (class | held because)
signature | Signed path requires issuer_key_id and issuer_signature when pinned keys/key record supplied; verifies canonical JSON excluding only issuer_signature and timestamp_utc: verifier.py:313-353; signing uses same region: envelope.py:509-511.
tamper / checked-but-unsigned fields | not_after and decision_id excluded from decision_sha256 but included in signature region: envelope.py:133-148, 503-511; verifier checks signature before reassert: verifier.py:313-353.
freshness | Envelope not_after rejects malformed/naive/expired: verifier.py:368-379; signed published-record freshness rejects stale not_after: published_record_source.py:175-183.
manifest / anchor pinning | Byte-anchor mode refuses if fetched bytes hash != pinned root before parsing: published_source.py:115-128; target refuses None record: reference_target.py:272-277.
replay R-01 | Threadpool race closed for one sidecar process: shared cache is app state authz_sidecar.py:260-263, used through ExecutorGate at 300-312; InMemoryReplayCache holds a threading.Lock across prune/check/set: replay_cache.py:105-128. Boundary: cross-process exactly-once requires Redis/shared store, replay_cache.py:193-203.
duplicate headers P-01 | Sidecar duplicate interaction header returns absent: authz_sidecar.py:209-220; sidecar duplicate envelope header returns absent: authz_sidecar.py:277-287; reference target duplicate envelope header returns absent: reference_target.py:245-253. No remaining first-wins path found.

Scope check: grounded the break and held checks only in IMPLEMENTATION/. Did not assert root/cloud/TLS compromise, caller bypass outside routing, semantic action wisdom, or DoS.
