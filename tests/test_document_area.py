from backend.app.document_area import AreaDocument, propose
from tests.test_api import setup_session
from tests.cycle_helpers import approve_and_review

def test_area_requires_explicit_valid_bounds():
    for text in ['Brasília e arredores', 'AREA_EXERCICIO_WGS84: 10,20,-10,30', 'AREA_EXERCICIO_WGS84: 0,86,1,89']:
        assert propose(AreaDocument(pages=[{'page':1,'text':text}]))['candidates'] == []
    doc=AreaDocument(pages=[{'page':2,'text':'AREA_EXERCICIO_WGS84: -48,-16,-47,-15'}])
    assert propose(doc)['candidates'][0]['bounds'] == [-48,-16,-47,-15]

def test_area_confirmation_permissions_persistence_and_lock(tmp_path, monkeypatch):
    c,sid,h=setup_session(tmp_path,monkeypatch)
    base=f'/api/sessions/{sid}'
    body={'pages':[{'page':2,'text':'AREA_EXERCICIO_WGS84: -48,-16,-47,-15'}]}
    before=c.get(base,headers=h['instrutor']).json()
    assert c.post(base+'/document-area/propose',json=body,headers=h['instrutor']).status_code==200
    assert c.get(base,headers=h['instrutor']).json()==before
    assert c.post(base+'/document-area/confirm',json=body,headers=h['azul']).status_code==403
    confirmed=c.post(base+'/document-area/confirm',json=body,headers=h['instrutor'])
    assert confirmed.status_code==200
    assert confirmed.json()['units']==before['units']
    assert c.get(base,headers=h['instrutor']).json()['document_area']['page']==2
    assert 'document_area' not in c.get(base,headers=h['azul']).json()
    token=approve_and_review(c,sid,h['instrutor'])
    assert c.post(base+'/turns',json={'token':token},headers=h['instrutor']).status_code==200
    assert c.post(base+'/document-area/confirm',json=body,headers=h['instrutor']).status_code==400
