"""
Domain-semantic validity D(I, domain) for Elyon-Sol.

The forward-direction invariant (docs/design/domain_validity_D_architecture.md;
docs/design/future_directions_domain_semantic_evaluation.md). Where G(I) answers
"is this interaction ADMISSIBLE?" (authority AC^3, coverage T^26, continuity CCS),
D answers a strictly-later question about an ALREADY-admissible interaction:
"is the content carried inside its envelope SEMANTICALLY VALID within its declared
domain?". The target composition, adopted openly at a canon-version event (GR-1):

    G(I) = AC^3 AND T^26 AND CCS AND D(I, domain)

===============================================================================
Build-then-wire / default-off (GR-2)
===============================================================================

This module is ABOVE G(I) and imports NOTHING from evaluator.py's hashed core.
It is UNWIRED: evaluator.decide()/pep.governed_call do not call it, so
evaluator_sha256, manifest_sha256, canon_sha256 and the published record are
byte-unchanged and the default admissibility path is byte-behavior-identical.
Composing D into the decision is a deliberate, canon-ratified step (VL-115
re-pin discipline), not a side effect of adding this file.

===============================================================================
Determinism and fail-closed (load-bearing)
===============================================================================

D is a deterministic predicate evaluator over a hash-pinnable domain manifest,
NOT a model and NOT a policy-engine runtime. The canon's determinism guarantee
(section 9 reproducibility) is load-bearing: identical (interaction, domain
manifest) always yields the identical verdict. Every malformation, unknown
domain, or unresolvable required field fails CLOSED (INVALID). A non-deterministic
or Rego-style D would be a different, weaker system; that line is held here.

===============================================================================
Recursive assessment of envelope content
===============================================================================

D assesses the interaction's domain payload - the `context` sub-object of the
normalized interaction, which is exactly what build_envelope records under
request_context.context. Predicate `path`s address fields by dotted key,
walked RECURSIVELY into nested objects. This is the "recursive assessment of
envelope content" the interaction carries: the check reaches into the data the
admissible envelope contains, not merely the top-level authority/coverage sets.

===============================================================================
Why D guards against rubber-stamping
===============================================================================

Inside the admissible state, a human oversight approval (the 202 PENDING_APPROVAL
grant path) could rubber-stamp an authorized action whose *content* is invalid or
unsafe for its domain. D is a deterministic gate the human cannot wave through:
composed as `eligible <=> G(I) AND D`, a domain-invalid interaction is REFUSED
even with a valid authority set and a signed human grant. Policy adherence is thus
enforced on the data inside the envelope, not assumed from the approval. See the
architecture doc for the domain-drift -> out-of-band re-determination outcome
(distinct from reassert()'s RE-EVALUATE-REQUIRED), which routes a mid-stream
domain-compliance change into the existing signed-grant path.

===============================================================================
Reason-code namespace (D_) - disjoint from G_ and REF_
===============================================================================

D emits a closed set of D_ codes naming WHICH domain condition failed, DISJOINT
by prefix from the evaluator's G_ vocabulary (evaluator.py) and the boundary/
transport REF_* vocabulary (pep/verifier/authz_sidecar). The module owns the
closed code set; a predicate may carry a human-readable `label` for diagnostics,
but the returned code is always from this module's set, preserving disjointness.

assess() is the single source of truth (state, code, detail); domain_valid() and
domain_reason() are thin projections - one evaluation, three views - mirroring the
evaluator's decide()/evaluate()/refusal_reason() discipline (VL-150).
"""

import hashlib
import json
from typing import Any, Dict, Optional, Tuple

# Example (NON-armed) domain manifest. Nothing loads this by default; callers
# pass a domain manifest explicitly (as pep passes the manifest to decide()).
DOMAIN_MANIFEST_EXAMPLE_PATH = "MANIFEST/domain_manifest.example.json"


# ---------------------------------------------------------------------------
# Domain-validity reason codes (closed set; D_ namespace disjoint from G_/REF_)
# ---------------------------------------------------------------------------

D_MANIFEST_MALFORMED = "D_MANIFEST_MALFORMED"    # domain manifest not well-formed
D_DOMAIN_UNKNOWN = "D_DOMAIN_UNKNOWN"            # declared domain absent from an armed manifest
D_DOMAIN_UNDECLARED = "D_DOMAIN_UNDECLARED"      # armed manifest + require_domain, none declared
D_DOMAIN_MISBOUND = "D_DOMAIN_MISBOUND"          # declared domain not bound to the interaction type
D_FIELD_ABSENT = "D_FIELD_ABSENT"                # a `present` predicate's path did not resolve
D_FIELD_INVALID = "D_FIELD_INVALID"              # an equals/in/not_in/absent predicate failed
D_INTERNAL = "D_INTERNAL"                         # fail-closed catch-all

# The closed rule vocabulary. A small, deterministic predicate set - NOT a rule
# engine. Extending it is a deliberate design act, not an author-manifest freedom.
_RULES = frozenset({"present", "absent", "equals", "in", "not_in"})

# Sentinel distinguishing "path did not resolve" from "resolved to null".
_MISSING = object()


# ---------------------------------------------------------------------------
# Domain manifest hashing (pinning primitive; NOT yet wired into the record)
# ---------------------------------------------------------------------------


def domain_manifest_sha256(path: str) -> str:
    """SHA-256 hex of a domain manifest file's bytes.

    The pinning primitive so a domain ruleset is hash-verifiable exactly like
    MANIFEST/manifest.json (canon 11.9). Wiring this into published_hashes.json
    (a new domain_manifest_sha256 pin) is deferred to the canon-increment step -
    adding it now would move the published record and RED the verify-against-
    pinned family (VL-115), which is the compose-in step, not this build step.
    """
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_domain_manifest(path: str = DOMAIN_MANIFEST_EXAMPLE_PATH) -> Dict[str, Any]:
    """Load a domain manifest from disk. Not called on any default path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Structural validation (fail-closed)
# ---------------------------------------------------------------------------


def _valid_predicate(p: Any) -> bool:
    """A predicate is {path: str, rule: <closed vocab>, [value], [label]}."""
    if not isinstance(p, dict):
        return False
    path = p.get("path")
    if not isinstance(path, str) or not path:
        return False
    rule = p.get("rule")
    if rule not in _RULES:
        return False
    if rule == "equals" and "value" not in p:
        return False
    if rule in ("in", "not_in") and not isinstance(p.get("value"), list):
        return False
    if "label" in p and not isinstance(p["label"], str):
        return False
    return True


def safe_domain_manifest(dm: Any) -> Optional[Dict[str, Any]]:
    """Return dm if well-formed, else None (fail-closed).

    Shape:
      {
        "version": "1.0",
        "require_domain": <bool, optional>,        # default False
        "domains": {
          "<domain-name>": {
            "predicates": [ {path, rule, [value], [label]}, ... ]
          }, ...
        }
      }
    A manifest with no `domains` key (or an empty map) is well-formed but
    UNARMED: D is a no-op pass-through, mirroring the flat/default manifest in
    the typed-impact machinery (evaluator.resolve_required_sets).
    """
    if not isinstance(dm, dict):
        return None
    if not isinstance(dm.get("version"), str):
        return None
    if "require_domain" in dm and not isinstance(dm["require_domain"], bool):
        return None
    domains = dm.get("domains")
    if domains is None:
        return dm  # unarmed
    if not isinstance(domains, dict):
        return None
    for dname, spec in domains.items():
        if not isinstance(dname, str) or not isinstance(spec, dict):
            return None
        preds = spec.get("predicates")
        if not isinstance(preds, list):
            return None
        for p in preds:
            if not _valid_predicate(p):
                return None
        # S3: out-of-band domain-verdict requirement (additive, fail-closed).
        # A domain MAY declare `requires_verdict: true`, meaning an admissible
        # interaction in this domain must ALSO carry a valid signed verdict from
        # the pinned policy authority (domain_control HOLD_FOR_VERDICT until then).
        # When true, `authority_key_id` (the pinned trusted signer) is MANDATORY -
        # a requires_verdict domain with no pinned authority is a manifest error.
        rv = spec.get("requires_verdict")
        if rv is not None and not isinstance(rv, bool):
            return None
        # DV-02: optional domain<->interaction_type binding (list of str tokens).
        bt = spec.get("interaction_types")
        if bt is not None:
            if not isinstance(bt, list) or not all(isinstance(x, str) and x for x in bt):
                return None
        if "authority_key_id" in spec and not isinstance(spec["authority_key_id"], str):
            return None
        if rv is True and not (isinstance(spec.get("authority_key_id"), str)
                               and spec["authority_key_id"]):
            return None
    return dm


# ---------------------------------------------------------------------------
# Recursive path resolution + predicate evaluation
# ---------------------------------------------------------------------------


def _resolve_path(content: Any, path: str) -> Any:
    """Walk a dotted path recursively into nested dicts. _MISSING if unresolved.

    Dict-only descent is deliberate: it keeps resolution total and deterministic
    (no list-index ambiguity, no attribute access). A path into a non-dict, or a
    missing key, resolves to _MISSING (fail-closed for value predicates)."""
    cur = content
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def _same_value(a: Any, b: Any) -> bool:
    """Strict value equality for compliance predicates (DV-06 mitigation).

    Python's bool IS an int subclass, so `1 == True` and `False in [0, 1, 2]`.
    For a deterministic compliance check that is a semantic hole: a payload
    carrying `consent: 1` would satisfy `equals: true`. Require the bool-ness of
    both operands to agree, then compare by value (so int/float 1 vs 1.0 still
    compares numerically, which is JSON-reasonable, but never bool-vs-number)."""
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def _eval_predicate(content: Any, p: Dict[str, Any]) -> bool:
    """True iff the predicate holds over `content`. Assumes _valid_predicate(p)."""
    val = _resolve_path(content, p["path"])
    rule = p["rule"]
    if rule == "present":
        return val is not _MISSING and val is not None
    if rule == "absent":
        return val is _MISSING or val is None
    # value predicates on a missing field fail closed:
    if val is _MISSING:
        return False
    if rule == "equals":
        return _same_value(val, p["value"])
    if rule == "in":
        return any(_same_value(val, x) for x in p["value"])
    if rule == "not_in":
        return not any(_same_value(val, x) for x in p["value"])
    return False  # unreachable given _valid_predicate gating


# ---------------------------------------------------------------------------
# assess() - single source of truth
# ---------------------------------------------------------------------------


def assess(ctx: Any, domain_manifest: Any) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
    """Domain-semantic validity verdict for an interaction.

    Returns (state, code, detail):
      state  - "VALID" or "INVALID"
      code   - a D_ code naming the FIRST failing condition on INVALID, else None
      detail - optional dict locating the failure (domain/path/rule/label), else None

    Deterministic and fail-closed. The domain payload assessed is ctx["context"]
    (the envelope's request_context.context). Predicates short-circuit on the
    first failure, in list order.
    """
    try:
        dm = safe_domain_manifest(domain_manifest)
        if dm is None:
            return "INVALID", D_MANIFEST_MALFORMED, None

        domains = dm.get("domains") or {}
        if not domains:
            # Unarmed manifest: D is a no-op pass-through (byte-behavior-safe).
            return "VALID", None, None

        declared = ctx.get("domain") if isinstance(ctx, dict) else None
        if declared is None:
            # DV-01 mitigation - the default is now FAIL-CLOSED. Previously an
            # armed manifest PASSED an interaction that simply declared no
            # domain, so any caller could suppress every domain predicate AND
            # the requires_verdict gate by OMISSION. An armed manifest therefore
            # now demands a declared domain unless the deployment explicitly
            # opts out with require_domain: false (an eyes-open, recorded choice,
            # not a silent default). Matches the repo's fail-toward-oversight
            # precedent (resolve_required_sets under a typed manifest).
            if dm.get("require_domain") is False:
                return "VALID", None, None
            return "INVALID", D_DOMAIN_UNDECLARED, None

        spec = domains.get(declared)
        if not isinstance(spec, dict):
            return "INVALID", D_DOMAIN_UNKNOWN, {"domain": declared}

        # DV-02 mitigation - domain-shopping. The declared domain is CALLER
        # input; without a binding, a caller carrying healthcare-shaped content
        # could declare a weaker armed domain and skip the strict predicates and
        # the verdict requirement. A domain MAY therefore pin `interaction_types`
        # (the same token the manifest/evaluator resolve required sets by): the
        # caller's declared interaction_type must then be in that set, so the
        # domain is bound to WHAT the interaction is, not to what it claims.
        # Absent the pin the domain is unbound (backward-compatible); binding is
        # the deployment's explicit act.
        bound_types = spec.get("interaction_types")
        if isinstance(bound_types, list):
            itype = ctx.get("interaction_type") if isinstance(ctx, dict) else None
            if itype not in bound_types:
                return "INVALID", D_DOMAIN_MISBOUND, {
                    "domain": declared, "interaction_type": itype,
                }

        content = ctx.get("context")
        if not isinstance(content, dict):
            content = {}

        for p in spec.get("predicates", []):
            if not _eval_predicate(content, p):
                code = D_FIELD_ABSENT if p["rule"] == "present" else D_FIELD_INVALID
                return "INVALID", code, {
                    "domain": declared,
                    "path": p["path"],
                    "rule": p["rule"],
                    "label": p.get("label"),
                }

        return "VALID", None, None

    except Exception:
        return "INVALID", D_INTERNAL, None


# ---------------------------------------------------------------------------
# Projections (mirror evaluate()/refusal_reason())
# ---------------------------------------------------------------------------


def domain_valid(ctx: Any, domain_manifest: Any) -> bool:
    """True iff D(I, domain) holds. Projection of assess()[0]."""
    return assess(ctx, domain_manifest)[0] == "VALID"


def domain_reason(ctx: Any, domain_manifest: Any) -> Optional[str]:
    """The D_ reason code for this interaction, or None if VALID. Projection."""
    return assess(ctx, domain_manifest)[1]
