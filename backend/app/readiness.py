"""Indicador de prontidão DIDÁTICO de organizações fictícias.

Não estima poder de combate real, eficiência de armas nem baixas. A política
de bloqueio é uma regra convencional do jogo, não uma norma doutrinária.
"""
from __future__ import annotations

READINESS_VERSION = "readiness-teaching-v1"
STOP_THRESHOLD = 25
WARNING_THRESHOLD = 50


def status(value: int) -> str:
    if value <= STOP_THRESHOLD:
        return "indisponivel"
    if value <= WARNING_THRESHOLD:
        return "atencao"
    return "disponivel"


def normalize_unit(unit: dict) -> dict:
    """Permite compatibilidade com partidas antigas sem este indicador."""
    value = unit.get("readiness", 100)
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        value = 100
    return {**unit, "readiness": value, "readiness_status": status(value),
            "available_for_simulated_actions": value > STOP_THRESHOLD}


def unit_state(units: list[dict]) -> list[dict]:
    return [normalize_unit(unit) for unit in units]


def apply_training_variation(unit: dict, change: int) -> dict:
    """Altera apenas a variável abstrata; não calcula perdas ou ação militar."""
    if isinstance(change, bool) or not isinstance(change, int) or not -100 <= change <= 100:
        raise ValueError("Variação didática inválida")
    current = normalize_unit(unit)
    result = max(0, min(100, current["readiness"] + change))
    # Unidade indisponível continua bloqueada até que haja recuperação explícita.
    return normalize_unit({**current, "readiness": result})


def can_participate(unit: dict) -> bool:
    return normalize_unit(unit)["available_for_simulated_actions"]


def advance_turn(units: list[dict], turn: int) -> tuple[list[dict], list[dict]]:
    """Erosão de 3 pontos/turno, inteiramente inventada para o exercício.

    Não representa fadiga ou perdas reais nem parâmetros de combate.
    O bloqueio é automático e persiste até ajuste pedagógico explícito.
    """
    updated = []
    events = []
    for unit in units:
        previous = normalize_unit(unit)
        current = apply_training_variation(previous, -3)
        updated.append(current)
        if previous["available_for_simulated_actions"] and not current["available_for_simulated_actions"]:
            events.append({
                "kind": "unit_unavailable", "turn": turn, "unit_id": unit["id"],
                "rule": READINESS_VERSION,
                "cause": "Índice didático atingiu o limite de indisponibilidade",
                "before": previous["readiness"], "after": current["readiness"],
            })
    return updated, events
