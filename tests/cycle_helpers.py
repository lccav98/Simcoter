def approve_and_review(client,sid,headers):
    state=client.get(f"/api/sessions/{sid}",headers=headers).json()
    keys=("id","name","party","kind","echelon","x","y","readiness")
    body=dict(revision=state.get("preparation",{}).get("revision",0),fictional=True,action="approve",
              units=[{k:u[k] for k in keys} for u in state["units"]],
              information=[dict(category=c,description="Exemplo",source="Teste",validity="Turno 0",certainty="hipotese")
                           for c in ("terreno","clima","adversario","civis")])
    body.update({k:"Teste fictício" for k in ("objective","situation","instructions","constraints","support","coordination")})
    assert client.post(f"/api/sessions/{sid}/preparation",json=body,headers=headers).status_code==200
    return client.get(f"/api/sessions/{sid}/turn-review",headers=headers).json()["token"]
