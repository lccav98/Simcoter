"""Problemas pedagógicos derivados de indicadores e relatórios do cenário.

Não usa IA generativa, probabilidades de combate ou dados reais. Regras declarativas
e rastreáveis fornecem base para uma futura camada opcional de narração local.
"""
from __future__ import annotations

import hashlib
import json

RULES_VERSION = "context-v1"


def suggested_problems(state: dict) -> list[dict]:
    """Devolve problemas sem alterar o estado. Sempre inclui evidência verificável."""
    resources = state["resources"]
    turn = state["turn"]
    proposals: list[dict] = []
    for key, value in resources.items():
        if value <= 75:
            evidence = f"resources.{key}={value} no turno {turn}"
            proposals.append({
                "id": f"review-{key}-{turn}", "category": "logistica",
                "title": f"Revisão didática de recursos: {key}",
                "summary": f"O indicador fictício de {key} chegou a {value}/100. Revisar a coerência entre previsão e disponibilidade.",
                "evidence": [evidence], "trigger": "indicador <= 75",
                "question": "Quais premissas documentais devem ser revistas?",
                "rule": RULES_VERSION,
            })
    pending = [feature["id"] for feature in state["features"] if feature["status"] == "proposed"]
    if pending and turn >= 1:
        proposals.append({
            "id": f"pending-overlays-{turn}", "category": "planejamento",
            "title": "Medidas gráficas ainda não aprovadas",
            "summary": f"Há {len(pending)} medidas propostas que permanecem pendentes após o início do exercício.",
            "evidence": [f"features.{item}.status=proposed" for item in pending],
            "trigger": "turno >= 1 e medidas pendentes",
            "question": "Quais registros e aprovações precisam ser conferidos?",
            "rule": RULES_VERSION,
        })
    reports = state["reports"]
    if len(reports) >= 2:
        latest = reports[-2:]
        if latest[0]["party"] != latest[1]["party"]:
            proposals.append({
                "id": f"visibility-review-{latest[0]['id'][:8]}-{latest[1]['id'][:8]}",
                "category": "informacao",
                "title": "Conferência de visibilidade de relatórios",
                "summary": "Registros recentes pertencem a partidos diferentes. Conferir permissões antes de compartilhar sínteses.",
                "evidence": [f"reports.{r['id']}" for r in latest],
                "trigger": "relatórios de partidos distintos",
                "question": "Quais informações são acessíveis a cada participante?",
                "rule": RULES_VERSION,
            })
    return proposals


def context_digest(state: dict) -> str:
    """Hash estável para identificar contexto consultado na geração."""
    snapshot = {
        "turn": state["turn"], "resources": state["resources"],
        "features": [(f["id"], f["status"]) for f in state["features"]],
        "reports": [(r["id"], r["party"]) for r in state["reports"]],
    }
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def analyze_context(state: dict) -> dict:
    return {
        "session_id": state["id"], "turn": state["turn"],
        "context_hash": context_digest(state),
        "generation_mode": "deterministic_rules_no_llm",
        "problems": suggested_problems(state),
        "notes": "Propostas educacionais geradas apenas com evidências do estado registrado. Não são ordens operacionais.",
    }
