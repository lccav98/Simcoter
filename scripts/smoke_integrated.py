"""Smoke test HTTP do pacote compilado, para CI e verificação local.

Execute após npm run build + instalação Python: python scripts/smoke_integrated.py
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def request(base: str, path: str, method: str = "GET", body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if body is None else json.dumps(body).encode()
    req = Request(base + path, data=data, method=method, headers=headers)
    with urlopen(req, timeout=3) as response:
        payload = response.read()
        return response.status, response.headers.get("content-type", ""), payload


def main():
    if not (ROOT / "frontend" / "dist" / "index.html").is_file():
        raise RuntimeError("Primeiro execute: cd frontend && npm run build")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["SIMCOTER_DB"] = str(Path(tmp) / "smoke.sqlite3")
        env["SIMCOTER_AI_ENABLED"] = "false"
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.main:app",
             "--host", "127.0.0.1", "--port", str(port)],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        try:
            for _ in range(80):
                if proc.poll() is not None:
                    raise RuntimeError("Servidor terminou durante o teste")
                try:
                    if request(base, "/api/health")[0] == 200:
                        break
                except (URLError, TimeoutError):
                    time.sleep(0.1)
            else:
                raise RuntimeError("Servidor não respondeu ao health check")
            status, content_type, body = request(base, "/")
            assert status == 200 and "html" in content_type.lower()
            assert b"root" in body and b"SIMCOTER" in body
            status, _, created_body = request(base, "/api/sessions", "POST",
                                               {"title":"Smoke test integrado","seed":123})
            assert status == 200
            created = json.loads(created_body)
            sid = created["session"]["id"]
            token = created["credentials"]["instrutor"]
            status, _, body = request(base, f"/api/sessions/{sid}", token=token)
            assert status == 200 and json.loads(body)["id"] == sid
            status, _, body = request(base, f"/api/sessions/{sid}/turns", "POST", token=token)
            assert status == 200 and json.loads(body)["turn"] == 1
            status, _, body = request(base, f"/api/sessions/{sid}/staff/tasks", "POST",
                                       {"agent":"E4"}, token=token)
            assert status == 200 and json.loads(body)["summary"]["proposed"] == 1
            status, _, body = request(base, f"/api/sessions/{sid}/apa", token=token)
            assert status == 200 and json.loads(body)["turns"] == 1
            print("OK: HTTP frontend + API + turno + EMV + APA integrados")
        finally:
            proc.terminate()
            try:
                proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate(timeout=5)


if __name__ == "__main__":
    main()
