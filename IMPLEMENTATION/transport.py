"""
G5 transport-configuration seam (docs/restructure/12_g5_transport_design.md
step 1).

Purpose: let the two real HTTP hops of the gate - the gate-to-target push
(pep.py) and the published-record fetch (published_source.py) - run over either
loopback HTTP (dev / single box) or real socket + TLS (cross-host) with the ONLY
difference being CONFIGURATION (the TLS verification policy and an optional
client certificate), never code. This is the seam artifact 12 names so that the
same code path serves the single-box runner and the two-node harness.

Build-then-wire (the project discipline since VL-025): this module has NO callers
at the commit that introduces it. pep.py and published_source.py are NOT changed
here; wiring them to call post_to_target / get_published - with default arguments,
which produce byte-identical requests to the current direct requests.post /
requests.get calls - is the step that lands the two-node harness (artifact 12
steps 2-4). Introducing the seam first, with a runner that proves it, mirrors
VL-025 (envelope.py built with no caller) and VL-037 (verifier.py built with no
caller).

No new canonical invariant (canon section 14): transport is verification I/O.
This module only configures HOW bytes move; it never touches WHAT the gate
decides or WHAT the target verifies. The decision and the envelope contract are
unchanged.

Fail-closed (canon section 9): TLS verification defaults to ON. With no argument
and no environment override, _resolve_verify returns True, which is requests'
own default - so an unverifiable peer raises requests.exceptions.SSLError and the
caller's existing try/except (pep.governed_call's upstream catch;
published_source.fetch_published_record's `except Exception: return None`) maps
it to a fail-closed refusal, exactly as the un-TLS'd calls do today. The seam
never weakens verification by default; weakening requires an explicit caller
argument or an explicit environment value.

Custody (parallel to pep._get_signing_key and the out-of-band published-record
anchor): TLS material is resolved from the environment, never from the repo.
  ELYON_TLS_CA_BUNDLE   - path to a CA bundle the client trusts (the
                          cross-host case; a real-ish CA per artifact 12 step 3).
  ELYON_TLS_CLIENT_CERT  - "certfile" for a single combined cert, or
                          "certfile:keyfile" for mutual TLS. Absent = no client
                          cert (the default; one-way TLS).

Byte-identical default contract (the load-bearing property a wiring step relies
on): post_to_target(url, json_body, headers) with no TLS arguments and no
environment override issues exactly
    requests.post(url, json=json_body, headers=headers, verify=True, cert=None,
                  timeout=10)
which is behaviorally identical to pep.py's current
    requests.post(url, json=..., headers=..., timeout=10)
because requests already defaults verify=True and cert=None. Likewise
get_published(url) equals published_source.py's current
    requests.get(url, timeout=timeout).
The proof runner asserts this resolution explicitly.
"""

import os
from typing import Any, Dict, Optional, Tuple, Union

import requests


# Environment variable names for out-of-band TLS material (never in the repo).
ENV_CA_BUNDLE = "ELYON_TLS_CA_BUNDLE"
ENV_CLIENT_CERT = "ELYON_TLS_CLIENT_CERT"


def _resolve_verify(verify: Optional[Union[bool, str]]) -> Union[bool, str]:
    """
    Resolve the requests `verify` argument, fail-closed by default.

    Precedence: an explicit caller argument wins; then the ELYON_TLS_CA_BUNDLE
    environment path; then True (requests' default, full verification). The
    function never returns False on its own - disabling verification requires a
    caller to pass verify=False explicitly, which is a deliberate, visible act.
    """
    if verify is not None:
        return verify
    ca = os.environ.get(ENV_CA_BUNDLE)
    if ca:
        return ca
    return True


def _resolve_cert(
    client_cert: Optional[Union[str, Tuple[str, str]]],
) -> Optional[Union[str, Tuple[str, str]]]:
    """
    Resolve the requests `cert` argument (client certificate for mutual TLS).

    Precedence: an explicit caller argument wins; then ELYON_TLS_CLIENT_CERT
    ("certfile" or "certfile:keyfile"); then None (no client cert). None is the
    requests default, so the byte-identical default contract holds.
    """
    if client_cert is not None:
        return client_cert
    cc = os.environ.get(ENV_CLIENT_CERT)
    if not cc:
        return None
    if ":" in cc:
        certfile, keyfile = cc.split(":", 1)
        return (certfile, keyfile)
    return cc


def post_to_target(
    url: str,
    json_body: Any,
    headers: Dict[str, str],
    *,
    verify: Optional[Union[bool, str]] = None,
    client_cert: Optional[Union[str, Tuple[str, str]]] = None,
    timeout: int = 10,
) -> requests.Response:
    """
    The gate-to-target push hop, transport-configured.

    Equivalent to pep.governed_call's current
        requests.post(target_url, json=normalized_interaction,
                      headers={"X-Elyon-Sol-Envelope": ...}, timeout=10)
    when called with default TLS arguments and no environment override. The body
    and header contract are unchanged; only the TLS verification policy and an
    optional client certificate are added, resolved fail-closed.
    """
    return requests.post(
        url,
        json=json_body,
        headers=headers,
        verify=_resolve_verify(verify),
        cert=_resolve_cert(client_cert),
        timeout=timeout,
    )


def get_published(
    url: str,
    *,
    verify: Optional[Union[bool, str]] = None,
    timeout: int = 10,
) -> requests.Response:
    """
    The published-record fetch hop, transport-configured.

    Equivalent to published_source.fetch_published_record's current
        requests.get(publisher_url, timeout=timeout)
    when called with default TLS arguments and no environment override. The
    anchor-verification of the returned bytes is NOT done here (it stays in
    published_source.load_record_from_bytes per that module's separation of
    concerns); this function only performs the transport-configured GET.
    """
    return requests.get(
        url,
        verify=_resolve_verify(verify),
        timeout=timeout,
    )
