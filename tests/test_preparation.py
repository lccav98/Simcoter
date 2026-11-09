from backend.app.preparation import Preparation
from tests.test_api import setup_session
import pytest

def payload():
    return dict(revision=0,fictional=True,action="draft",objective="Estudo fictício",
                units=[dict(id="nova",name="Unidade fictícia",party="azul",x=20,y=20,readiness=80)],
                information=[])

def test_preparation_persistence_access_revision_and_application(tmp_path,monkeypatch):
    client,sid,headers=setup_session(tmp_path,monkeypatch)
    url=f"/api/sessions/{sid}/preparation"
    body=payload()
    assert client.post(url,json=body,headers=headers["azul"]).status_code==403
    saved=client.post(url,json=body,headers=headers["instrutor"]).json()
    assert saved["preparation"]["revision"]==1
    assert saved["units"][0]["id"]!="nova"
    assert "preparation" not in client.get(f"/api/sessions/{sid}",headers=headers["azul"]).json()
    assert client.post(url,json=body,headers=headers["instrutor"]).status_code==400
    body.update(revision=1,action="approve",situation="Fictícia",instructions="Revisar fontes",constraints="Somente exercício",support="Abstrato",coordination="Instrutor")
    body["information"]=[dict(category=c,description="Condição fictícia",source="Instrutor",validity="Turno 0",certainty="hipotese") for c in ["terreno","clima","adversario","civis"]]
    result=client.post(url,json=body,headers=headers["instrutor"])
    assert result.status_code==200,result.text
    assert result.json()["units"][0]["id"]=="nova"
    assert len(result.json()["preparation_history"])==2
    client.post(f"/api/sessions/{sid}/turns",json={"token":client.get(f"/api/sessions/{sid}/turn-review",headers=headers["instrutor"]).json()["token"]},headers=headers["instrutor"])
    body["revision"]=2
    assert client.post(url,json=body,headers=headers["instrutor"]).status_code==400

def test_preparation_rejects_cycle():
    body=payload()
    body["units"][0]["parent"]="nova"
    with pytest.raises(ValueError): Preparation(**body)
