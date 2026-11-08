from fastapi.testclient import TestClient

from backend.app import main
from backend.app.game import GameStore


def test_api_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", GameStore(tmp_path / "api.sqlite3"))
    client = TestClient(main.app)
    assert client.get("/api/health").json()["ai_required"] is False
    response = client.post("/api/sessions", json={"title": "Teste", "seed": 123})
    assert response.status_code == 200
    game = response.json()
    game_id = game["id"]
    response = client.post(
        f"/api/sessions/{game_id}/reports",
        json={"source": "E4", "party": "azul", "message": "Teste fictício"},
    )
    assert response.status_code == 200
    assert len(response.json()["reports"]) == 1
    assert client.post(f"/api/sessions/{game_id}/features/ponto-1/approve").status_code == 200
    assert client.post(f"/api/sessions/{game_id}/turns").json()["turn"] == 1
    assert client.get(f"/api/sessions/{game_id}/apa").json()["report_count"] == 1


def test_missing_game(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", GameStore(tmp_path / "api.sqlite3"))
    client = TestClient(main.app)
    assert client.get("/api/sessions/inexistente").status_code == 404
