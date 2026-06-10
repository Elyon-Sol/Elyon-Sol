# Elyon-Sol service image (C1 / VL-081). One image serves any of the three
# uvicorn entrypoints (gate / target / publisher) by command override in
# docker-compose.yml. UNVALIDATED in the build sandbox (no docker); the stand-up
# is the author's (artifact 13 C1, locus AUTHOR).
FROM python:3.13-slim

WORKDIR /app

# Pinned runtime deps (cryptography pinned per VL-040; the gate's HTTP + crypto
# stack). No test/dev deps in the runtime image.
RUN pip install --no-cache-dir \
    "cryptography==44.0.0" \
    "fastapi" \
    "uvicorn" \
    "requests"

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

ENV PYTHONPATH=/app

# Default command (the gate); overridden per service in docker-compose.yml.
CMD ["uvicorn", "IMPLEMENTATION.pep:app", "--host", "0.0.0.0", "--port", "8000"]
