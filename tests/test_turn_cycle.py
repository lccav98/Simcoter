from tests.test_api import setup_session
from tests.cycle_helpers import approve_and_review

def test_immediate_movement_cannot_bypass_review(tmp_path, monkeypatch):
    c, sid, h = setup_session(tmp_path, monkeypatch)
    auth = h["instrutor"]
    url = f"/api/sessions/{sid}"
    token = approve_and_review(c, sid, auth)
    for expected_turn in (0, 1):
        before = c.get(url, headers=auth).json()
        assert before["turn"] == expected_turn
        rejected = c.post(url + "/units/azul-1/movement", headers=auth,
                          json={"x":40, "y":50, "authorized":True})
        assert rejected.status_code == 400
        assert c.get(url, headers=auth).json() == before
        if expected_turn == 0:
            assert c.post(url + "/turns", headers=auth, json={"token":token}).status_code == 200

def test_cycle_gates_and_duplicate(tmp_path,monkeypatch):
    c,sid,h=setup_session(tmp_path,monkeypatch);auth=h["instrutor"];url=f"/api/sessions/{sid}"
    assert c.post(url+"/turns",json={},headers=auth).status_code==400
    token=approve_and_review(c,sid,auth)
    assert c.post(url+"/turns",json={"token":token},headers=h["azul"]).status_code==403
    response=c.post(url+"/turns",json={"token":token},headers=auth)
    assert response.status_code==200
    assert response.json()["turn"]==1
    assert c.post(url+"/turns",json={"token":token},headers=auth).status_code==400
    assert c.get(url,headers=auth).json()["turn"]==1

def test_orders_revalidate_and_execute_atomically(tmp_path,monkeypatch):
    c,sid,h=setup_session(tmp_path,monkeypatch);auth=h["instrutor"];url=f"/api/sessions/{sid}"
    approve_and_review(c,sid,auth)
    c.post(url+"/orders/azul-1",json={"x":40,"y":50},headers=auth)
    before=c.get(url,headers=auth).json()
    assert before["units"][0]["x"]==23
    token=c.get(url+"/turn-review",headers=auth).json()["token"]
    c.post(url+"/environment/weather",json={"weather":"severe"},headers=auth)
    assert c.post(url+"/turns",json={"token":token},headers=auth).status_code==400
    assert c.get(url,headers=auth).json()["units"][0]["x"]==23
    c.post(url+"/environment/weather",json={"weather":"normal"},headers=auth)
    token=c.get(url+"/turn-review",headers=auth).json()["token"]
    result=c.post(url+"/turns",json={"token":token},headers=auth).json()
    assert result["units"][0]["x"]==40 and result["orders"]==[]
    assert any(e["kind"]=="turn_reviewed" for e in result["events"])

def test_changed_report_invalidates_review(tmp_path,monkeypatch):
    c,sid,h=setup_session(tmp_path,monkeypatch);auth=h["instrutor"];url=f"/api/sessions/{sid}"
    token=approve_and_review(c,sid,auth)
    c.post(url+"/reports",json={"source":"Exemplo","message":"Mudança","party":"instrutor"},headers=auth)
    assert c.post(url+"/turns",json={"token":token},headers=auth).status_code==400
