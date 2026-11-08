"""Restrições de tabuleiro fictício: clima, terreno, prontidão e auditoria."""
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.environment import grade_at, movement_check
from backend.app.game import GameStore


def test_fictitious_zones_and_weather_rules():
    unit={"readiness":70}
    assert grade_at(50,30)=="impeditivo"
    assert grade_at(65,65)=="restritivo"
    assert grade_at(10,10)=="livre"
    assert movement_check(unit,50,30,"normal",True)["allowed"] is False
    assert movement_check(unit,65,65,"normal",False)["review_required"] is True
    assert movement_check(unit,65,65,"normal",False)["allowed"] is False
    assert movement_check(unit,65,65,"normal",True)["allowed"] is True
    assert movement_check(unit,10,10,"severe",True)["allowed"] is False
    assert movement_check(unit,10,10,"adverse",False)["allowed"] is False
    assert movement_check(unit,10,10,"adverse",True)["allowed"] is True
    assert movement_check({"readiness":20},10,10,"normal",True)["allowed"] is False
    with pytest.raises(ValueError):
        grade_at(-1,20)
    with pytest.raises(ValueError):
        movement_check(unit,10,10,"not-weather")


def test_api_environment_and_staff_do_not_mutate_without_approval(tmp_path, monkeypatch):
    store=GameStore(tmp_path/"environment.sqlite3")
    monkeypatch.setattr(main,"store",store)
    client=TestClient(main.app)
    created=client.post("/api/sessions",json={}).json()
    sid=created["session"]["id"]
    instructor={"Authorization":"Bearer "+created["credentials"]["instrutor"]}
    blue={"Authorization":"Bearer "+created["credentials"]["azul"]}
    env_path=f"/api/sessions/{sid}/environment"
    assert client.get(env_path).status_code==401
    assert client.get(env_path,headers=blue).status_code==403
    env=client.get(env_path,headers=instructor)
    assert env.status_code==200
    assert len(env.json()["zones"])==2

    weather=client.post(env_path+"/weather",headers=instructor,
                        json={"weather":"severe"})
    assert weather.status_code==200
    assert weather.json()["weather"]=="severe"
    forbidden=client.post(
        f"/api/sessions/{sid}/units/azul-1/movement", headers=blue,
        json={"x":10,"y":10,"authorized":True},
    )
    assert forbidden.status_code==403
    path=f"/api/sessions/{sid}/units/azul-1/movement"
    assert client.post(path,headers=instructor,
                       json={"x":10,"y":10,"authorized":True}).status_code==400
    assert store.get(sid)["units"][0]["x"]==23

    client.post(env_path+"/weather",headers=instructor,json={"weather":"normal"})
    assert client.post(path,headers=instructor,
                       json={"x":50,"y":30,"authorized":True}).status_code==400
    assert client.post(path,headers=instructor,
                       json={"x":65,"y":65,"authorized":False}).status_code==400
    check=client.post(path+"/check",headers=instructor,
                      json={"x":65,"y":65,"authorized":True})
    assert check.status_code==200 and check.json()["allowed"] is True
    moved=client.post(path,headers=instructor,
                      json={"x":65,"y":65,"authorized":True})
    assert moved.status_code==200
    assert moved.json()["units"][0]["x"]==65
    assert moved.json()["events"][-1]["kind"]=="fictitious_move"

    # Agentes E3/E4 recebem somente clima e contagens resumidas.
    for agent in ("E3","E4"):
        assigned=client.post(f"/api/sessions/{sid}/staff/tasks",headers=instructor,
                             json={"agent":agent})
        assert assigned.status_code==200
        task=assigned.json()["tasks"][-1]
        assert task["evidence"]["weather"]=="normal"
        assert "unavailable_count" in task["evidence"]
        assert "units" not in task["evidence"]
