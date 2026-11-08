#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "Python com pip é obrigatório" >&2
  exit 2
fi
python3 -m pip install -e '.[test]'
(cd frontend && npm install && npm run build)
python3 scripts/start_local.py
