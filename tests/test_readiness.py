"""Prontidão sintética; nunca representa poder de combate ou perdas reais."""
from fastapi.testclient import TestClient
import pytest

from backend.app import main
from backend.app.game import GameStore
from backend.app.readiness import (
    STOP_THRESHOLD, READINESS_VERSION, status, can_participate,
    apply_training_variation,
)


def test_readiness_boundaries():
    assert status(26) == "atencao"
    assert status(25) == "indisponivel"
    assert status(50) == "atencao"
    assert status(51) == "disponivel"
    for value in (-200, 200, True):
        with pytest.raises(ValueError):
            apply_training_variation({"readiness":70}, value)


def test_auto_blocks_and_does_not_reenable_without_review(tmp_path):
    store=GameStore(tmp_path/"readiness.db")
    sid=store.create(seed=123)["id"]
    before=store.validate_unit_action(sid,"azul-2")
    assert before["allowed"] is True
    # Valor inicial fictício 65; atualização arbitrária de -3 por turno.
    for _ in range(14):
        last=store.next_turn(sid)
    availability=store.validate_unit_action(sid,"azul-2")
    assert availability["readiness"] == 23
    assert availability["status"] == "indisponivel"
    assert availability["allowed"] is False
    assert any(e["kind"]=="unit_unavailable" and e["unit_id"]=="azul-2"
               for e in last["events"])
    later=store.next_turn(sid)
    assert later["units"][1]["available_for_simulated_actions"] is False
    assert store.apa(sid)["unit_readiness"][1]["status"]=="indisponivel"
    recovery=store.unit_readiness(sid,"azul-2",20)
    assert recovery["units"][1]["available_for_simulated_actions"] is True
    assert store.validate_unit_action(sid,"azul-2")["allowed"] is True


def test_api_protects_review_and_other_party_status(tmp_path,monkeypatch):
    store=GameStore(tmp_path/"readiness_api.db")
    monkeypatch.setattr(main,"store",store)
    client=TestClient(main.app)
    created=client.post("/api/sessions",json={}).json()
    sid=created["session"]["id"]
    headers={role:{"Authorization":f"Bearer {token}"}
             for role,token in created["credentials"].items()}
    endpoint=f"/api/sessions/{sid}/units/azul-1/readiness"
    assert client.post(endpoint,json={"change":-100},
                       headers=headers["vermelha"]).status_code==403
    assert client.get(f"/api/sessions/{sid}/units/azul-1/availability",
                      headers=headers["vermelha"]).status_code==404
    response=client.post(endpoint,json={"change":-100},headers=headers["instrutor"])
    assert response.status_code==200
    assert response.json()["units"][0]["readiness"]==0
    assert client.get(f"/api/sessions/{sid}/units/azul-1/availability",
                      headers=headers["azul"]).json()["allowed"] is False
    assert client.get(f"/api/sessions/{sid}/units/azul-1/availability",
                      headers=headers["instrutor"]).json()["rule"]==READINESS_VERSION
    visible=client.get(f"/api/sessions/{sid}",headers=headers["vermelha"]).json()
    assert len(visible["units"])==1
    assert visible["units"][0]["id"]=="vermelha-1"
