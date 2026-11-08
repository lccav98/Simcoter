"""Testes HTTP do modelo experimental de tokens por partida."""
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.game import GameStore


def setup_session(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "store", GameStore(tmp_path / "api.sqlite3"))
    client = TestClient(main.app)
    response = client.post("/api/sessions", json={"title": "Teste", "seed": 123})
    assert response.status_code == 200
    created = response.json()
    session_id = created["session"]["id"]
    tokens = created["credentials"]
    headers = {role: {"Authorization": f"Bearer {token}"} for role, token in tokens.items()}
    return client, session_id, headers


def test_api_flow(tmp_path, monkeypatch):
    client, session_id, headers = setup_session(tmp_path, monkeypatch)
    assert client.get("/api/health").json()["ai_required"] is False
    report = client.post(
        f"/api/sessions/{session_id}/reports",
        json={"source": "E4", "message": "Teste fictício"},
        headers=headers["azul"],
    )
    assert report.status_code == 200
    assert len(report.json()["reports"]) == 1
    assert client.post(
        f"/api/sessions/{session_id}/features/ponto-1/approve",
        headers=headers["instrutor"],
    ).status_code == 200
    assert client.post(
        f"/api/sessions/{session_id}/turns", headers=headers["instrutor"]
    ).json()["turn"] == 1
    assert client.get(
        f"/api/sessions/{session_id}/apa", headers=headers["instrutor"]
    ).json()["report_count"] == 1


def test_missing_and_invalid_credentials(tmp_path, monkeypatch):
    client, session_id, headers = setup_session(tmp_path, monkeypatch)
    assert client.get(f"/api/sessions/{session_id}").status_code == 401
    assert client.get(
        f"/api/sessions/{session_id}",
        headers={"Authorization": "Bearer token-invalido"},
    ).status_code == 403
    assert client.get(
        "/api/sessions/inexistente", headers=headers["instrutor"]
    ).status_code == 403


def test_parties_are_isolated(tmp_path, monkeypatch):
    client, session_id, headers = setup_session(tmp_path, monkeypatch)
    blue_secret = "RELATORIO AZUL RESERVADO"
    red_secret = "RELATORIO VERMELHO RESERVADO"
    assert client.post(
        f"/api/sessions/{session_id}/reports",
        headers=headers["azul"], json={"source": "E2", "message": blue_secret},
    ).status_code == 200
    assert client.post(
        f"/api/sessions/{session_id}/reports",
        headers=headers["vermelha"], json={"source": "E4", "message": red_secret},
    ).status_code == 200
    blue = client.get(f"/api/sessions/{session_id}", headers=headers["azul"])
    red = client.get(f"/api/sessions/{session_id}", headers=headers["vermelha"])
    instructor = client.get(f"/api/sessions/{session_id}", headers=headers["instrutor"])
    assert red_secret not in blue.text
    assert blue_secret not in red.text
    assert blue_secret in instructor.text and red_secret in instructor.text
    assert len(blue.json()["units"]) == 2 and len(red.json()["units"]) == 1
    assert blue.json()["resources"] == {}
    assert "seed" not in red.json()
    assert red.json()["events"] == []


def test_party_cannot_impersonate_or_mutate_global_state(tmp_path, monkeypatch):
    client, session_id, headers = setup_session(tmp_path, monkeypatch)
    assert client.post(
        f"/api/sessions/{session_id}/reports",
        headers=headers["azul"],
        json={"source": "E2", "message": "Tentativa", "party": "vermelha"},
    ).status_code == 403
    assert client.post(
        f"/api/sessions/{session_id}/turns", headers=headers["azul"]
    ).status_code == 403
    assert client.post(
        f"/api/sessions/{session_id}/features/ponto-1/approve",
        headers=headers["vermelha"],
    ).status_code == 403
    for suffix in ("apa", "context", "probability", "ai/explanation"):
        assert client.get(
            f"/api/sessions/{session_id}/{suffix}", headers=headers["azul"]
        ).status_code == 403
    assert client.get(
        f"/api/sessions/{session_id}", headers=headers["instrutor"]
    ).json()["turn"] == 0


def test_ai_endpoint_fallback_without_external_service(tmp_path, monkeypatch):
    client, session_id, headers = setup_session(tmp_path, monkeypatch)
    monkeypatch.setenv("SIMCOTER_AI_ENABLED", "false")
    before = client.get(f"/api/sessions/{session_id}", headers=headers["instrutor"]).json()
    response = client.get(
        f"/api/sessions/{session_id}/ai/explanation", headers=headers["instrutor"]
    )
    assert response.status_code == 200
    assert response.json()["mode"] == "rules_fallback"
    assert response.json()["available"] is False
    after = client.get(f"/api/sessions/{session_id}", headers=headers["instrutor"]).json()
    assert before == after

def test_mutations_preserve_authenticated_instructor_role(tmp_path, monkeypatch):
    client, sid, headers = setup_session(tmp_path, monkeypatch)
    state = client.get(f"/api/sessions/{sid}", headers=headers["instrutor"]).json()
    unit_id = state["units"][0]["id"]
    actions = [
        ("turns", {}),
        ("features/ponto-1/approve", {}),
        (f"units/{unit_id}/readiness", {"change": -1}),
        ("environment/weather", {"weather": "normal"}),
    ]
    for path, body in actions:
        response = client.post(f"/api/sessions/{sid}/{path}", json=body, headers=headers["instrutor"])
        assert response.status_code == 200
        assert response.json()["role"] == "instrutor"
        denied = client.post(f"/api/sessions/{sid}/{path}", json=body, headers=headers["azul"])
        assert denied.status_code == 403
