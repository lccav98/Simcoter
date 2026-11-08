#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
(cd frontend && npm install && npm run build)
.venv/bin/python scripts/start_local.py
