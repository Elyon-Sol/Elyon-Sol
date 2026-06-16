# Example OPA policy for the SECOND ext_authz filter (opa-envoy) in Mode A.
#
# This is the POLICY layer ("does policy permit it?"), distinct from and
# downstream of the elyon-authz admissibility layer ("is this interaction
# admissible to be considered at all?"). By the time a request reaches this
# policy, elyon-authz has already ALLOWED it - the envelope is current, bound,
# signed, and not replayed. OPA then applies the deployment's own rules.
#
# The two layers never import each other; they compose only as ordered Envoy
# filters. This example default-denies and allows only GETs, purely to show the
# wiring - real deployments replace the rule body. opa-envoy calls the
# `elyon/authz/allow` decision (see docker-compose.authz.yml plugin path).
package elyon.authz

import rego.v1

default allow := false

# Allow read-only methods through the policy layer; everything else is denied
# HERE (admissibility was already enforced upstream by elyon-authz).
allow if {
	input.attributes.request.http.method == "GET"
}
