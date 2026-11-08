"""Regras didáticas de terreno e clima para TABULEIRO FICTÍCIO.

Sem geodados reais, modelos de mobilidade, itinerários ou eficiência militar.
A classificação é declarativa e os limites são escolhidos para o jogo.
"""
from __future__ import annotations

ENV_VERSION="environment-teaching-v1"
WEATHER={"normal":"Condições estáveis","adverse":"Condições adversas","severe":"Suspensão climática"}
ZONES=(
    {"id":"zone-blocked","label":"Área impeditiva fictícia","grade":"impeditivo",
     "bounds":{"x_min":45,"x_max":60,"y_min":20,"y_max":45}},
    {"id":"zone-restricted","label":"Área restritiva fictícia","grade":"restritivo",
     "bounds":{"x_min":58,"x_max":80,"y_min":57,"y_max":79}},
)


def grade_at(x:int,y:int)->str:
    if not isinstance(x,int) or isinstance(x,bool) or not isinstance(y,int) or isinstance(y,bool):
        raise ValueError("Coordenadas fictícias devem ser inteiras")
    if not (0<=x<=100 and 0<=y<=100):
        raise ValueError("Coordenadas fora da área fictícia")
    for zone in ZONES:
        b=zone["bounds"]
        if b["x_min"]<=x<=b["x_max"] and b["y_min"]<=y<=b["y_max"]:
            return zone["grade"]
    return "livre"


def movement_check(unit:dict,x:int,y:int,weather:str,authorized:bool=False)->dict:
    from .readiness import normalize_unit
    if weather not in WEATHER:
        raise ValueError("Condição climática inválida")
    terrain=grade_at(x,y)
    current=normalize_unit(unit)
    reasons=[]
    if not current["available_for_simulated_actions"]:
        reasons.append("Unidade indisponível pelo índice didático")
    if terrain=="impeditivo":
        reasons.append("Área impeditiva: deslocamento fictício bloqueado")
    if weather=="severe":
        reasons.append("Suspensão climática fictícia: deslocamento bloqueado")
    review=terrain=="restritivo" or weather=="adverse"
    if review and not authorized:
        reasons.append("Exige autorização explícita do instrutor")
    allowed=not reasons
    return {"allowed":allowed,"review_required":review,"terrain":terrain,
            "weather":weather,"reasons":reasons,
            "rule":ENV_VERSION,"destination":{"x":x,"y":y},
            "warning":"Política fictícia de tabuleiro, não previsão de mobilidade militar"}


def environment_view(weather:str)->dict:
    if weather not in WEATHER:
        raise ValueError("Condição climática inválida")
    return {"weather":weather,"weather_label":WEATHER[weather],
            "zones":[dict(zone) for zone in ZONES],"version":ENV_VERSION,
            "legend":{"livre":"Livre","restritivo":"Restritivo","impeditivo":"Impeditivo"}}
