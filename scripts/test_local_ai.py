"""Teste opcional de geração real, com banco temporário e autenticação."""
import argparse
import gc
import json
import os
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        os.environ["SIMCOTER_DB"] = str(Path(directory) / "smoke.sqlite3")
        os.environ["SIMCOTER_AI_ENABLED"] = "true"
        os.environ["SIMCOTER_OLLAMA_MODEL"] = args.model
        from fastapi.testclient import TestClient
        from backend.app.main import app
        with TestClient(app) as client:
            created = client.post("/api/sessions", json={"title": "Validação fictícia", "seed": 2026}).json()
            sid = created["session"]["id"]
            headers = {"Authorization": "Bearer " + created["credentials"]["instrutor"]}
            url = f"/api/sessions/{sid}/ai/explanation"
            assert client.get(url).status_code == 401
            assert client.get(url, headers={"Authorization": "Bearer " + created["credentials"]["azul"]}).status_code == 403
            before = client.get(f"/api/sessions/{sid}", headers=headers).json()
            started = time.monotonic()
            response = client.get(url, headers=headers)
            result = response.json()
            after = client.get(f"/api/sessions/{sid}", headers=headers).json()
            summary = {"model": args.model, "available": result.get("available"),
                       "mode": result.get("mode"), "seconds": round(time.monotonic()-started, 2),
                       "state_unchanged": before == after, "access_control": "passed"}
            print(json.dumps(summary))
            success = response.status_code == 200 and result.get("available") is True and before == after
        gc.collect()
        return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
