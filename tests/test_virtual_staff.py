"""Estado-Maior Virtual: funções delimitadas, aprovação humana e isolamento."""
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.game import GameStore
from backend.app.virtual_staff import AGENTS, PaperclipAdapter, create_proposal


def test_agents_use_only_relevant_evidence(tmp_path):
    store = GameStore(tmp_path / "staff.sqlite")
    created = store.create_with_credentials()
    sid = created["session"]["id"]
    state = store.report(sid, "Fonte A", "TEXTO RESERVADO", "azul")
    for role in AGENTS:
        task = create_proposal(state, role)
        assert task["agent"] == role
        assert task["status"] == "proposed"
        assert "TEXTO RESERVADO" not in str(task)
    assert set(create_proposal(state, "E4")["evidence"]) == {"resources", "turn"}
    assert "reports" not in create_proposal(state, "E3")["evidence"]


def test_staff_approval_changes_only_task_and_audit(tmp_path):
    store = GameStore(tmp_path / "staff.sqlite")
    sid = store.create_with_credentials()["session"]["id"]
    before = store.get(sid)
    result = store.staff_assign(sid, "E4")
    assert result["summary"]["proposed"] == 1
    task_id = result["tasks"][0]["id"]
    approved = store.staff_review(sid, task_id, "approved")
    assert approved["summary"]["approved"] == 1
    after = store.get(sid)
    assert after["resources"] == before["resources"]
    assert after["turn"] == before["turn"]
    assert len(after["events"]) == len(before["events"]) + 2
    with pytest.raises(ValueError):
        store.staff_review(sid, task_id, "rejected")


def test_staff_is_instructor_only(tmp_path, monkeypatch):
    store = GameStore(tmp_path / "staff_api.sqlite")
    monkeypatch.setattr(main, "store", store)
    client = TestClient(main.app)
    created = client.post("/api/sessions", json={}).json()
    sid, tokens = created["session"]["id"], created["credentials"]
    blue = {"Authorization": "Bearer " + tokens["azul"]}
    instructor = {"Authorization": "Bearer " + tokens["instrutor"]}
    assert client.get(f"/api/sessions/{sid}/staff", headers=blue).status_code == 403
    assert client.post(f"/api/sessions/{sid}/staff/tasks", headers=blue,
                       json={"agent": "E1"}).status_code == 403
    assert client.get(f"/api/sessions/{sid}/staff").status_code == 401
    result = client.post(f"/api/sessions/{sid}/staff/tasks",
                         headers=instructor, json={"agent": "E1"})
    assert result.status_code == 200
    task_id = result.json()["tasks"][0]["id"]
    assert client.post(f"/api/sessions/{sid}/staff/tasks/{task_id}/review",
                       headers=blue, json={"action": "approved"}).status_code == 403
    ok = client.post(f"/api/sessions/{sid}/staff/tasks/{task_id}/review",
                     headers=instructor, json={"action": "approved"})
    assert ok.status_code == 200
    assert ok.json()["summary"]["approved"] == 1


def test_paperclip_is_optional_stub(tmp_path):
    store = GameStore(tmp_path / "staff.sqlite")
    state = store.create()
    with pytest.raises(RuntimeError, match="não instalado"):
        PaperclipAdapter().propose(state, "E1")
    with pytest.raises(ValueError):
        create_proposal(state, "E9")


def test_invalid_review_does_not_mutate(tmp_path):
    store = GameStore(tmp_path / "staff.sqlite")
    sid = store.create_with_credentials()["session"]["id"]
    store.staff_assign(sid, "E2")
    before = store.get(sid)
    with pytest.raises(ValueError):
        store.staff_review(sid, before["staff_tasks"][0]["id"], "done")
    assert store.get(sid) == before
