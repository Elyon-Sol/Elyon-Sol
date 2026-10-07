#!/usr/bin/env bash
# Rebuild the git-ignored .venv in place, on the same Python and pins as CI
# (.github/workflows/ci.yml) and the image (deploy/Dockerfile), then prove it.
#
#   scripts/rebuild_venv.sh               # rebuild + suite + repo_health
#   scripts/rebuild_venv.sh --skip-tests  # rebuild only
#
# Run from anywhere; it works on the repository this script lives in. Every
# console script (pip, pytest, ...) gets a shebang for the CURRENT checkout path,
# which is what goes stale when the checkout moves (e.g. /home/elyon -> /elyon).
set -euo pipefail

PYTHON_VERSION=3.14
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$REPO/.venv"
cd "$REPO"

SKIP_TESTS=0
case "${1:-}" in
  --skip-tests) SKIP_TESTS=1 ;;
  "") ;;
  *) echo "usage: $0 [--skip-tests]" >&2; exit 2 ;;
esac

PY="$(command -v "python$PYTHON_VERSION" || true)"
if [ -z "$PY" ]; then
  echo "python$PYTHON_VERSION not found - CI and deploy/Dockerfile use $PYTHON_VERSION" >&2
  exit 1
fi

echo "== rebuilding $VENV with $("$PY" --version)"
"$PY" -m venv --clear "$VENV"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -r requirements-dev.txt

# The point of the rebuild: console scripts must run from this checkout path.
shebang="$(head -1 "$VENV/bin/pip")"
if [ "$shebang" != "#!$VENV/bin/python$PYTHON_VERSION" ] && [ "$shebang" != "#!$VENV/bin/python3" ] && [ "$shebang" != "#!$VENV/bin/python" ]; then
  echo "unexpected pip shebang: $shebang" >&2
  exit 1
fi
"$VENV/bin/pip" --version
"$VENV/bin/python" -m pip check

if [ "$SKIP_TESTS" -eq 1 ]; then
  echo "== rebuilt (tests skipped)"
  exit 0
fi

echo "== suite"
PYTHONPATH="$REPO" "$VENV/bin/python" -m pytest TESTS/ -q -p no:cacheprovider
echo "== repo_health"
"$VENV/bin/python" scripts/repo_health.py
echo "== rebuilt and verified"
