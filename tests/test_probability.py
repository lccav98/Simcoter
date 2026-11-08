"""Testes do MPS educacional. Não calcula resultados militares reais."""
import copy

import pytest

from backend.app.game import GameStore
from backend.app.probability import MODEL_VERSION, forecast, sample_transition


def test_same_seed_same_transition():
    resources = {"suprimentos": 90, "manutencao": 85, "transporte": 88, "saude": 92}
    a = sample_transition(resources, seed=2026, next_turn=1)
    b = sample_transition(resources, seed=2026, next_turn=1)
    assert a == b
    assert resources["manutencao"] == 85
    assert a["event"]["rule"] == MODEL_VERSION
    assert a["event"]["resource"] == "manutencao"


def test_no_event_without_context():
    resources = {"suprimentos": 100, "manutencao": 100, "transporte": 100, "saude": 100}
    result = sample_transition(resources, seed=1, next_turn=1)
    assert result["event"]["kind"] == "routine_turn"
    assert result["resources"]["suprimentos"] == 98


def test_severity_never_exceeds_fictitious_limits():
    resources = {"suprimentos": 74, "manutencao": 10, "transporte": 75, "saude": 80}
    for seed in range(50):
        result = sample_transition(resources, seed, next_turn=3)
        event = result["event"]
        assert event["kind"] == "scenario_event"
        assert 0 <= event["effect"] <= 3
        assert all(0 <= value <= resources[key] for key, value in result["resources"].items())


def test_forecast_does_not_mutate_session(tmp_path):
    store = GameStore(tmp_path / "mps.db")
    state = store.create(seed=5)
    before = copy.deepcopy(store.get(state["id"]))
    a = store.probability_preview(state["id"], repetitions=100)
    b = store.probability_preview(state["id"], repetitions=100)
    after = store.get(state["id"])
    assert a == b
    assert before == after
    assert sum(a["categories"].values()) == 100
    assert sum(a["severities"].values()) == 100
    assert a["model_version"] == MODEL_VERSION


@pytest.mark.parametrize("amount", [0, -1, 2001, 1.5, True])
def test_forecast_rejects_invalid_runs(amount):
    with pytest.raises(ValueError):
        forecast({"suprimentos": 70}, 1, 0, amount)


def test_forecast_at_turn_limit_is_rejected():
    with pytest.raises(ValueError):
        forecast({"suprimentos": 70}, 1, 20, 100)
