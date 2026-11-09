"""Ciclo auditável de tabuleiro, sem modelos militares."""
from hashlib import sha256
import json
from .environment import movement_check
from .probability import sample_transition
from .readiness import advance_turn

def fingerprint(state):
    return sha256(json.dumps(state,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def review(state):
    issues=[]
    if state.get("preparation",{}).get("status")!="approved":
        issues.append("Aprove a preparação inicial antes de iniciar.")
    if state["turn"]>=20:
        issues.append("Limite de 20 turnos alcançado.")
    outcomes=[]
    for order in state.get("orders",[]):
        unit=next((u for u in state["units"] if u["id"]==order["unit_id"]),None)
        if not unit:
            issues.append("Unidade da ordem não existe mais.")
            continue
        check=movement_check(unit,order["x"],order["y"],state["weather"],order["authorized"])
        if not check["allowed"]:
            issues.append(unit["name"]+": "+"; ".join(check["reasons"]))
        outcomes.append({"unit_id":unit["id"],"name":unit["name"],"destination":{"x":order["x"],"y":order["y"]},"allowed":check["allowed"]})
    transition=sample_transition(state["resources"],state["seed"],state["turn"]+1)
    units,_=advance_turn(state["units"],state["turn"]+1)
    return {"token":fingerprint(state),"turn":state["turn"]+1,"issues":issues,"orders":outcomes,
            "resources_before":state["resources"],"resources_after":transition["resources"],
            "event":transition["event"],"units_after":[{"id":u["id"],"readiness":u["readiness"]} for u in units],
            "warning":"Sem ordens, unidades permanecem nas posições. Validação apenas do destino; sem rota ou combate."}
