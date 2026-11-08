from backend.app.context import analyze_context, suggested_problems
from backend.app.doctrine import search_catalog
from backend.app.game import GameStore


def test_no_arbitrary_problems_at_start(tmp_path):
    store = GameStore(tmp_path / "start.sqlite3")
    state = store.create()
    assert suggested_problems(state) == []


def test_contextual_problem_has_evidence(tmp_path):
    store = GameStore(tmp_path / "progress.sqlite3")
    state = store.create(seed=100)
    for _ in range(8):
        state = store.next_turn(state["id"])
    result = analyze_context(state)
    assert result["generation_mode"] == "deterministic_rules_no_llm"
    assert result["context_hash"]
    assert result["problems"]
    for problem in result["problems"]:
        assert problem["evidence"]
        assert problem["trigger"]
        assert problem["rule"] == "context-v1"


def test_search_local_catalog_is_metadata_only():
    rows = search_catalog("logistica")
    assert len(rows) == 1
    assert rows[0]["code"] == "EB70-MC-10.238"
    assert "Pendente" in rows[0]["verification"]
    assert search_catalog("XXXX-NAO-EXISTE") == []


def test_context_problems_are_stable(tmp_path):
    store = GameStore(tmp_path / "stable.sqlite3")
    state = store.create(seed=11)
    for _ in range(2):
        state = store.next_turn(state["id"])
    a = analyze_context(state)
    b = analyze_context(store.get(state["id"]))
    assert a == b
