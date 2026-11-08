from pathlib import Path

import pytest

from backend.app.game import GameStore, INITIAL_RESOURCES


def test_create_and_reopen(tmp_path: Path):
    db_path = tmp_path / "game.sqlite3"
    state = GameStore(db_path).create(seed=42)
    assert state["turn"] == 0
    assert GameStore(db_path).get(state["id"])["seed"] == 42


def test_turns_are_reproducible(tmp_path: Path):
    store = GameStore(tmp_path / "game.sqlite3")
    ids = [store.create(seed=98)["id"] for _ in range(2)]
    for _ in range(4):
        a = store.next_turn(ids[0])
        b = store.next_turn(ids[1])
        assert a["resources"] == b["resources"]
        assert [e.get("name") for e in a["events"]] == [e.get("name") for e in b["events"]]


def test_report_and_apa_have_evidence(tmp_path: Path):
    store = GameStore(tmp_path / "game.sqlite3")
    state = store.create()
    state = store.report(state["id"], "E4 fictício", "Conferir estoque simulado", "azul")
    state = store.approve_feature(state["id"], "ponto-1")
    state = store.next_turn(state["id"])
    apa = store.apa(state["id"])
    assert apa["report_count"] == 1
    assert apa["approved_features"] == 1
    assert apa["turns"] == 1
    assert apa["events"][0]["rule"] == "simcoter-v1"
    assert set(apa["resource_variations"]) == set(INITIAL_RESOURCES)


def test_invalid_input_does_not_mutate(tmp_path: Path):
    store = GameStore(tmp_path / "game.sqlite3")
    session_id = store.create()["id"]
    with pytest.raises(ValueError):
        store.report(session_id, "E4", "Alerta", "indefinido")
    with pytest.raises(ValueError):
        store.approve_feature(session_id, "nao-existe")
    assert store.get(session_id)["events"] == []


def test_turn_limit(tmp_path: Path):
    store = GameStore(tmp_path / "game.sqlite3")
    session_id = store.create()["id"]
    for _ in range(20):
        store.next_turn(session_id)
    with pytest.raises(ValueError):
        store.next_turn(session_id)
