# Elyon-Sol service image (C1 / VL-081). One image serves any of the three
# uvicorn entrypoints (gate / target / publisher) by command override in
# docker-compose.yml. Built and run with every compose overlay except authz.tls on
# 2026-09-27 (Python 3.14.7 in the image).
FROM python:3.14-slim

WORKDIR /app

# Pinned runtime deps from the repo's requirements.txt (cryptography pinned per
# VL-040). No test/dev deps in the runtime image.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# The application code + the committed, hash-locked published record. Trust
# material (keys, the pinned anchor) is NOT baked in - it arrives by environment
# from the out-of-band .env (see deploy/bootstrap_config.py).
COPY IMPLEMENTATION/ /app/IMPLEMENTATION/
COPY EVIDENCE/published_hashes.json /app/EVIDENCE/published_hashes.json
# The signed-record (freshness) publisher endpoint generates the live pins, so the
# image needs the generator modules too (VL-092; the byte-anchor path serves only
# the static record above and does not). These import canon.lock / evaluator.py /
# manifest.json, all already copied.
COPY EVIDENCE/published_hashes_gen.py /app/EVIDENCE/published_hashes_gen.py
COPY EVIDENCE/published_hashes_signed_gen.py /app/EVIDENCE/published_hashes_signed_gen.py
COPY CANON/canon.lock /app/CANON/canon.lock
COPY MANIFEST/ /app/MANIFEST/
# The governance overlay runs deploy.governance.approver_trust_bootstrap:app.
COPY deploy/governance/approver_trust_bootstrap.py /app/deploy/governance/approver_trust_bootstrap.py

ENV PYTHONPATH=/app

# Default command (the gate); overridden per service in docker-compose.yml.
CMD ["uvicorn", "IMPLEMENTATION.pep:app", "--host", "0.0.0.0", "--port", "8000"]
