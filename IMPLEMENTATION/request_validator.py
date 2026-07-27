"""
Schema validator for the Elyon-Sol PEP boundary.

Implements SPEC/request_schema.md build-order step 3. Given an
already-parsed Python dict representing the incoming request body,
the validator returns either a normalized interaction dict (on
schema acceptance) or a refusal code (on schema rejection).

The validator does NOT touch IMPLEMENTATION/pep.py. Wiring this
validator into the PEP boundary is build-order step 4
(proposed VL-019), a separate commit per VL-011's lesson.

==============================================================
API contract (Candidate 3 from VL-017b, resolved)
==============================================================

The validator accepts an already-parsed Python ``dict``. JSON parsing
is the caller's (PEP's) responsibility. The spec's "PEP boundary
behavior" step 1 (parse JSON; failure -> REFUSE with
REF_SCHEMA_PARSE_ERROR) is a boundary concern, not a validator
concern: the validator cannot meaningfully fail on parse error
because its input is already parsed.

This resolves the VL-017b dry-run divergence:
- Grok routed REF_SCHEMA_PARSE_ERROR to "(handled outside validator)".
- OpenAI defined REF_SCHEMA_PARSE_ERROR as a constant and documented
  its non-emission inside the validator.

The validator here takes OpenAI's approach: REF_SCHEMA_PARSE_ERROR
is exported as a module-level constant so that the future pep.py
revision (VL-019) imports a single schema-vocabulary set; the
validator itself never emits it. The seven-code vocabulary of the
spec is preserved at the module level even though only six codes
are emit-points of this function. This makes the API/procedure
separation explicit rather than implicit.

==============================================================
Seventh code (Candidate 1 from VL-017b, resolved by coupling)
==============================================================

Because the validator takes a parsed dict, REF_SCHEMA_PARSE_ERROR
is structurally unreachable from inside this module. The seven
codes named in SPEC/request_schema.md "PEP boundary behavior"
are split:

- Six codes EMITTED by validate_request():
  REF_SCHEMA_TOP_LEVEL, REF_SCHEMA_BAD_URL, REF_SCHEMA_FLAT_KEYS,
  REF_SCHEMA_MANIFEST_PINNING_MISSING, REF_SCHEMA_RESERVED_CCS,
  REF_SCHEMA_TYPE_MISMATCH.

- One code NAMED HERE BUT EMITTED BY pep.py (VL-019):
  REF_SCHEMA_PARSE_ERROR. The PEP catches FastAPI/JSON-decode
  failure and converts to a 403 with this code. Centralizing the
  constant here makes the schema-layer vocabulary discoverable
  from one import.

==============================================================
Generic unknown keys inside `interaction` (Candidate 2 from
VL-017b, upgraded to real spec gap)
==============================================================

SPEC/request_schema.md "PEP boundary behavior" step 4 says
"no unknown top-level keys inside `interaction`" but only enumerates
refusal codes for two subclasses: CCS-shaped keys
(REF_SCHEMA_RESERVED_CCS) and flat-key collisions at the outer
level (REF_SCHEMA_FLAT_KEYS, which is about TOP-level keys, not
keys inside `interaction`). Non-CCS-shaped unknown keys inside
`interaction` have no enumerated code.

TESTS/adversarial/test_request_schema.py flagged this at module-
docstring lines 31-37 (VL-017's test author surfaced it). VL-017b's
dry-run surfaced it independently via OpenAI's gap-candidate
section (Candidate 2). Two independent surface events make this a
real spec gap, not a candidate; upgraded in VL-018's ledger entry
to a numbered artifact-04 row.

RESOLVED at VL-054 (Option A). Unknown non-CCS-shaped keys inside
`interaction` are refused with REF_SCHEMA_UNKNOWN_KEY, the code that
names the cause ("field is unexpected"). This replaces the VL-018
provisional mapping to REF_SCHEMA_TYPE_MISMATCH, whose natural
reading is "field type is wrong," not "field is unexpected." The
spec edit took option (a): SPEC/request_schema.md "Rejected shapes"
gains an "Unknown key inside `interaction`" entry naming
REF_SCHEMA_UNKNOWN_KEY (VL-054 spec commit). Option (b) (overloading
TYPE_MISMATCH) was rejected: the whole value of the fix is
vocabulary honesty, and the unknown-key path is a distinct emission
point (step 4d, the set difference below) separate from the step-5
type checks.

The validator does NOT fail-open on unknown keys (which would
violate the spec's step-4 prohibition); fail-closed is preserved.
The provisional mapping's cost (a slightly misleading refusal code)
is retired.

==============================================================
Validation order (load-bearing per spec PEP boundary behavior)
==============================================================

The order matches SPEC/request_schema.md "PEP boundary behavior,"
adapted for the parsed-dict input contract:

1. (PARSE - not this function's responsibility; handled in pep.py)
2. Top-level shape: target_url and interaction both present and of
   correct type. -> REF_SCHEMA_TOP_LEVEL
3. target_url syntactic validity (RFC 3986 absolute URL).
   -> REF_SCHEMA_BAD_URL
4a. Flat-key check: AP or OP at top level (alongside or instead of
    `interaction`). -> REF_SCHEMA_FLAT_KEYS
4b. CCS-shaped key check: any key (top-level or inside
    `interaction`) containing the substring "ccs" (case-insensitive)
    or matching the named continuity-token patterns
    (`continuity_token`, `prior_state_hash`).
    -> REF_SCHEMA_RESERVED_CCS
4c. Manifest pinning presence: expected_manifest_version and
    expected_manifest_sha256 both present in `interaction`.
    -> REF_SCHEMA_MANIFEST_PINNING_MISSING
4d. Unknown-key check inside `interaction` (resolved VL-054, see
    "Generic unknown keys" above). -> REF_SCHEMA_UNKNOWN_KEY
5. Type/format checks on each field. -> REF_SCHEMA_TYPE_MISMATCH

Ordering rationale: 4a before 4b before 4c before 4d. Flat-key is
checked before CCS because a request with both AP-at-top-level AND
a CCS-shaped field is more diagnostically clear as "flat-key
violation" than as "CCS-reserved violation" - the flat-key is the
structural problem, the CCS is a consequence-level problem. CCS
before pinning-missing because a CCS-shaped field signals a
specific G0-track violation that warrants explicit naming over a
generic missing-field message. Pinning-missing before unknown-key
because pinning is required and named; unknown-key is the
catch-all for keys outside the required set.

This is one specific deterministic ordering; alternative orderings
are defensible but a deterministic one is required so that diagnoses
are reproducible. Documented for future reference.

==============================================================
Return shape
==============================================================

Returns either:
  (None, refusal_code: str)        on refusal
  (normalized_interaction: dict, None)  on acceptance

The two-tuple is unambiguous: exactly one element is None. Callers
(pep.py at VL-019) destructure as `interaction, refusal = ...` and
branch on `refusal is not None`.

The normalized_interaction has AP and OP sorted (canonical-JSON
preparation for envelope embedding per open question 3 of the spec,
which recommends PEP normalization). All other fields pass through
unchanged.
"""

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Refusal codes (the seven-code schema vocabulary per
# SPEC/request_schema.md "PEP boundary behavior")
# ---------------------------------------------------------------------------

# Emitted by validate_request():
REF_SCHEMA_TOP_LEVEL = "REF_SCHEMA_TOP_LEVEL"
REF_SCHEMA_BAD_URL = "REF_SCHEMA_BAD_URL"
REF_SCHEMA_FLAT_KEYS = "REF_SCHEMA_FLAT_KEYS"
REF_SCHEMA_MANIFEST_PINNING_MISSING = "REF_SCHEMA_MANIFEST_PINNING_MISSING"
REF_SCHEMA_RESERVED_CCS = "REF_SCHEMA_RESERVED_CCS"
REF_SCHEMA_TYPE_MISMATCH = "REF_SCHEMA_TYPE_MISMATCH"
REF_SCHEMA_UNKNOWN_KEY = "REF_SCHEMA_UNKNOWN_KEY"

# NAMED here for VL-019's pep.py import; NOT emitted by validate_request()
# because the validator's input contract is a parsed dict. See module
# docstring "API contract" and "Seventh code" sections.
REF_SCHEMA_PARSE_ERROR = "REF_SCHEMA_PARSE_ERROR"


# Required fields inside `interaction`, per SPEC/request_schema.md
# "Top-level wire shape" and "Field-by-field."
_REQUIRED_INTERACTION_FIELDS = frozenset(
    {
        "AP",
        "OP",
        "context",
        "expected_manifest_version",
        "expected_manifest_sha256",
    }
)

# OPTIONAL fields inside `interaction` (additive; absent = pre-typed behavior).
# `interaction_type` (typed-impact, step 8.2) selects the manifest interaction
# type whose required sets the caller must cover; under a flat manifest it is
# carried but ignored by the evaluator. A caller may omit it entirely.
_OPTIONAL_INTERACTION_FIELDS = frozenset({"interaction_type"})

# Named continuity-token patterns (literal key matches), per
# SPEC/request_schema.md "CCS-shaped fields." These are matched
# exactly (case-sensitive) in addition to the case-insensitive
# "ccs" substring match.
_NAMED_CCS_KEYS = frozenset(
    {
        "continuity_token",
        "prior_state_hash",
    }
)


def _is_ccs_shaped(key: str) -> bool:
    """
    Return True iff `key` is reserved by the CCS rule:
      - case-insensitive substring "ccs" anywhere in the key, OR
      - exact match against a named continuity-token pattern.

    Per SPEC/request_schema.md "CCS-shaped fields":
      'Any field whose key contains the substring `ccs`
      (case-insensitive) or makes a continuity assertion (e.g.,
      a `prior_state_hash`, `continuity_token`, `ccs_valid`).'
    """
    if "ccs" in key.lower():
        return True
    if key in _NAMED_CCS_KEYS:
        return True
    return False


def _is_absolute_url(value: Any) -> bool:
    """
    RFC 3986 absolute URL check, per SPEC/request_schema.md
    `target_url` field.

    An absolute URL has a scheme AND a netloc. Bare strings like
    "/target" (relative) or "127.0.0.1:9000/target" (no scheme;
    urlparse treats "127.0.0.1" as scheme and "9000/target" as
    path, but this fails the netloc test) are rejected.
    """
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = urlparse(value)
    except (ValueError, TypeError):
        return False
    return bool(parsed.scheme) and bool(parsed.netloc)


def _is_lowercase_hex_64(value: Any) -> bool:
    """
    64-character lowercase hex string check per
    SPEC/request_schema.md `interaction.expected_manifest_sha256`.

    Schema text (line 159): '<64-char lowercase hex string>'.
    Uppercase hex is rejected (covered by test
    type_mismatch_sha256_uppercase). Wrong length is rejected
    (covered by test type_mismatch_sha256_wrong_length).
    """
    if not isinstance(value, str):
        return False
    if len(value) != 64:
        return False
    # All lowercase hex digits 0-9 and a-f only.
    return all(c in "0123456789abcdef" for c in value)


def _is_array_of_strings(value: Any) -> bool:
    """
    Array-of-strings check per SPEC/request_schema.md `AP` and `OP`
    field definitions: "array of strings, required."
    """
    if not isinstance(value, list):
        return False
    return all(isinstance(item, str) for item in value)


def _normalize_set_field(value: List[str]) -> List[str]:
    """
    Canonical-JSON preparation per SPEC/request_schema.md open
    question 3 (recommended: PEP normalizes). Deduplicate (set
    semantics per section 11.5/11.6) and sort for deterministic
    serialization.
    """
    return sorted(set(value))


def validate_request(
    body: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate a parsed request body against SPEC/request_schema.md.

    Args:
        body: An already-parsed Python dict from the request payload.
              Parse errors are NOT this function's responsibility;
              see module docstring "API contract."

    Returns:
        On acceptance: (normalized_interaction, None) where
            normalized_interaction is the request's `interaction`
            field with AP and OP sorted and deduplicated.

        On refusal: (None, refusal_code) where refusal_code is one of
            the six emitted REF_SCHEMA_* constants exported by this
            module.

    The function does NOT raise on schema violations. All violations
    produce a refusal-code return. The caller (pep.py at VL-019)
    converts the refusal code to an HTTP 403 with detail payload
    {"terminal_state": "REFUSE", "refusal_reason_code": <code>}.

    The function does NOT call evaluate(). Schema validation
    precedes evaluation per the spec's PEP boundary behavior; the
    fail-closed invariant ("an unevaluatable request is a refused
    request") is preserved by returning a refusal-code without
    side effects.
    """
    # ----- Step 2: Top-level shape -----
    # body itself must be a dict (the caller should pass a dict;
    # this guard catches programming errors and arrays/strings/None
    # arriving at the boundary).
    if not isinstance(body, dict):
        return None, REF_SCHEMA_TOP_LEVEL

    # ----- Step 4a: Flat-key check (G2 closure) -----
    # AP or OP at the TOP LEVEL is the archived interception_proof
    # shape. Checked BEFORE top-level-shape's interaction-presence
    # check so that the flat-key diagnosis takes precedence over a
    # missing-interaction diagnosis when both are true.
    #
    # Per SPEC/request_schema.md "Flat-key payload": 'A request with
    # AP or OP at the top level is treated as schema-malformed
    # regardless of any other fields present.'
    if "AP" in body or "OP" in body:
        return None, REF_SCHEMA_FLAT_KEYS

    # ----- Step 4b: CCS-shaped keys at TOP level -----
    # Per SPEC/request_schema.md "CCS-shaped fields": any CCS-shaped
    # key REFUSED regardless of nesting. Top-level check happens
    # before interaction-shape because a legacy ccs_valid at top
    # level (archived interception_proof shape) should be diagnosed
    # as CCS-reserved rather than as a generic unknown top-level
    # key.
    for key in body.keys():
        if key in ("target_url", "interaction"):
            continue
        if _is_ccs_shaped(key):
            return None, REF_SCHEMA_RESERVED_CCS

    # ----- Step 2 (continued): target_url and interaction presence -----
    if "target_url" not in body or "interaction" not in body:
        return None, REF_SCHEMA_TOP_LEVEL

    interaction = body["interaction"]
    if not isinstance(interaction, dict):
        return None, REF_SCHEMA_TOP_LEVEL

    # ----- Step 3: target_url syntactic validity -----
    target_url = body["target_url"]
    if not _is_absolute_url(target_url):
        return None, REF_SCHEMA_BAD_URL

    # ----- Step 4b (continued): CCS-shaped keys INSIDE interaction -----
    # CCS-shaped key inside `interaction` is checked before pinning-
    # missing because a CCS-shaped field is a specific G0-track
    # violation whose explicit naming is more diagnostically useful
    # than a "field absent" message.
    for key in interaction.keys():
        if _is_ccs_shaped(key):
            return None, REF_SCHEMA_RESERVED_CCS

    # ----- Step 4c: Manifest pinning presence -----
    # Per SPEC/request_schema.md "Missing manifest pinning": both
    # expected_manifest_version and expected_manifest_sha256 must
    # be present. Either absent -> REFUSE.
    if (
        "expected_manifest_version" not in interaction
        or "expected_manifest_sha256" not in interaction
    ):
        return None, REF_SCHEMA_MANIFEST_PINNING_MISSING

    # ----- Step 4d: Unknown keys inside interaction -----
    # See module docstring "Generic unknown keys inside interaction"
    # for the rationale. CCS-shaped keys have already been caught
    # above (step 4b inside-interaction); whatever reaches here is
    # an unknown non-CCS-shaped key. Resolved at VL-054 (Option A):
    # emit REF_SCHEMA_UNKNOWN_KEY, the code that names the cause,
    # replacing the provisional REF_SCHEMA_TYPE_MISMATCH mapping
    # VL-018 used as the closest extant code. Spec:
    # SPEC/request_schema.md "Rejected shapes" -> "Unknown key
    # inside interaction."
    unknown_keys = (set(interaction.keys())
                    - _REQUIRED_INTERACTION_FIELDS - _OPTIONAL_INTERACTION_FIELDS)
    if unknown_keys:
        return None, REF_SCHEMA_UNKNOWN_KEY

    # ----- Step 5: Type/format checks -----
    # AP, OP: arrays of strings.
    if not _is_array_of_strings(interaction["AP"]):
        return None, REF_SCHEMA_TYPE_MISMATCH
    if not _is_array_of_strings(interaction["OP"]):
        return None, REF_SCHEMA_TYPE_MISMATCH

    # context: object (dict). The schema does not constrain the
    # keys or values inside context; it must be a dict, possibly
    # empty.
    if not isinstance(interaction["context"], dict):
        return None, REF_SCHEMA_TYPE_MISMATCH

    # expected_manifest_version: string. The schema does not
    # constrain the format beyond "string"; the version comparison
    # is string equality at the evaluator layer.
    if not isinstance(interaction["expected_manifest_version"], str):
        return None, REF_SCHEMA_TYPE_MISMATCH

    # expected_manifest_sha256: 64-character lowercase hex.
    if not _is_lowercase_hex_64(interaction["expected_manifest_sha256"]):
        return None, REF_SCHEMA_TYPE_MISMATCH

    # interaction_type (OPTIONAL): a string when present. Absent -> untyped
    # (the evaluator defaults to the top-level required sets).
    if "interaction_type" in interaction and not isinstance(
        interaction["interaction_type"], str
    ):
        return None, REF_SCHEMA_TYPE_MISMATCH

    # ----- Accept -----
    # Normalize AP and OP (sort + dedupe) for canonical JSON
    # serialization downstream per open question 3 of the spec.
    # All other fields pass through unchanged.
    normalized = {
        "AP": _normalize_set_field(interaction["AP"]),
        "OP": _normalize_set_field(interaction["OP"]),
        "context": interaction["context"],
        "expected_manifest_version": interaction["expected_manifest_version"],
        "expected_manifest_sha256": interaction["expected_manifest_sha256"],
    }
    if "interaction_type" in interaction:
        normalized["interaction_type"] = interaction["interaction_type"]
    return normalized, None
