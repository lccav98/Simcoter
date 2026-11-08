"""Inicialização de uma única aplicação SIMCOTER em localhost.

Antes de executar:
    pip install -e '.[test]'
    cd frontend && npm install && npm run build
Depois:
    python scripts/start_local.py

O frontend compilado e a API passam a compartilhar http://127.0.0.1:8000.
A versão 0.8 NÃO deve ser publicada em rede LAN/internet.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    index = ROOT / "frontend" / "dist" / "index.html"
    if not index.is_file():
        print("ERRO: frontend ainda não compilado.", file=sys.stderr)
        print("Entre em frontend e execute: npm install && npm run build", file=sys.stderr)
        return 2
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print("ERRO: instale primeiro: pip install -e '.[test]'", file=sys.stderr)
        return 2
    print("SIMCOTER 0.8 — execução individual LOCAL")
    print("Abra: http://127.0.0.1:8000")
    print("A versão atual NÃO deve ser exposta à internet ou à LAN.")
    return subprocess.call(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
