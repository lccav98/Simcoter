"""Caminho integrado 0.8 — backend, MPS, EMV, APA e autorização.

Não exige Ollama ou internet. O teste de navegador/MapLibre/WebGL é separado,
pois o mapa-base público é online e o ambiente CI não inclui Safari iPadOS.
"""
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.game import GameStore


def test_complete_exercise_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", GameStore(tmp_path / "complete.sqlite"))
    monkeypatch.setenv("SIMCOTER_AI_ENABLED", "false")
    client = TestClient(main.app)

    assert client.get("/api/health").status_code == 200
    created_response = client.post(
        "/api/sessions", json={"title": "Exercício integrado 0.8", "seed": 2026}
    )
    assert created_response.status_code == 200
    created = created_response.json()
    sid = created["session"]["id"]
    headers = {
        role: {"Authorization": f"Bearer {token}"}
        for role, token in created["credentials"].items()
    }

    # Partidos separados e relatório fictício sem acesso cruzado.
    blue = client.post(
        f"/api/sessions/{sid}/reports", headers=headers["azul"],
        json={"source": "E1 fictício", "message": "Registro exclusivamente Azul"},
    )
    assert blue.status_code == 200
    red = client.get(f"/api/sessions/{sid}", headers=headers["vermelha"])
    assert "Registro exclusivamente Azul" not in red.text

    # Medida do mapa é aprovada apenas pelo instrutor.
    denied = client.post(
        f"/api/sessions/{sid}/features/ponto-1/approve", headers=headers["azul"]
    )
    assert denied.status_code == 403
    approved = client.post(
        f"/api/sessions/{sid}/features/ponto-1/approve",
        headers=headers["instrutor"],
    )
    assert approved.status_code == 200
    assert any(f["id"] == "ponto-1" and f["status"] == "approved"
               for f in approved.json()["features"])

    # MPS: previsão não altera a partida.
    before = client.get(f"/api/sessions/{sid}", headers=headers["instrutor"]).json()
    prediction = client.get(
        f"/api/sessions/{sid}/probability?repetitions=50",
        headers=headers["instrutor"],
    )
    assert prediction.status_code == 200
    assert prediction.json()["repetitions"] == 50
    after = client.get(f"/api/sessions/{sid}", headers=headers["instrutor"]).json()
    assert after == before

    # Avanço de turno e EMV usam o mesmo estado persistido.
    progressed = client.post(f"/api/sessions/{sid}/turns", headers=headers["instrutor"])
    assert progressed.status_code == 200
    assert progressed.json()["turn"] == 1

    assigned = client.post(
        f"/api/sessions/{sid}/staff/tasks", headers=headers["instrutor"],
        json={"agent": "E4"},
    )
    assert assigned.status_code == 200
    task = assigned.json()["tasks"][0]
    assert task["status"] == "proposed"
    reviewed = client.post(
        f"/api/sessions/{sid}/staff/tasks/{task['id']}/review",
        headers=headers["instrutor"], json={"action": "approved"},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["summary"]["approved"] == 1

    # A IA desligada não bloqueia o exercício.
    ai = client.get(f"/api/sessions/{sid}/ai/explanation", headers=headers["instrutor"])
    assert ai.status_code == 200 and ai.json()["mode"] == "rules_fallback"

    apa = client.get(f"/api/sessions/{sid}/apa", headers=headers["instrutor"])
    assert apa.status_code == 200
    assert apa.json()["turns"] == 1
    assert apa.json()["approved_features"] == 1
    assert apa.json()["report_count"] == 1


def test_public_doctrine_only_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", GameStore(tmp_path / "complete.sqlite"))
    client = TestClient(main.app)
    result = client.get("/api/doctrine?q=logistica")
    assert result.status_code == 200
    assert result.json()["mode"] == "metadata_only"
    assert result.json()["verified_citations"] is False
