"""MPS: probabilidades fictícias, condicionadas ao estado e reproduzíveis.

Este módulo é exclusivamente pedagógico. Não estima resultados de combate,
taxas de baixas, eficácia de armamentos ou probabilidade real de vitória.
Sem serviços externos, IA generativa ou bibliotecas pagas.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from typing import Any

MODEL_VERSION = "mps-educacional-v1"
THRESHOLD = 85
SEVERITIES = (
    ("leve", 1, 25),
    ("moderada", 2, 50),
    ("acentuada", 3, 25),
)
# Indicadores do jogo não correspondem a fatores doutrinários reais.
EVENT_CATALOG = (
    ("Atraso administrativo no recebimento de materiais", "suprimentos"),
    ("Indisponibilidade temporária de equipamento de apoio", "manutencao"),
    ("Interrupção fictícia de infraestrutura", "transporte"),
    ("Demanda adicional de atendimento em exercício", "saude"),
)


def _draw(seed: int, turn: int, tag: str, bound: int) -> int:
    """Geração estável; sha256 dispensa dependências externas e estado global."""
    if bound < 1:
        raise ValueError("Limite inválido")
    payload = f"{MODEL_VERSION}|{seed}|{turn}|{tag}".encode("utf-8")
    return int.from_bytes(sha256(payload).digest()[:8], "big") % bound


def baseline_resources(resources: dict[str, int]) -> dict[str, int]:
    """Desconto pedagógico uniforme e explícito realizado em cada turno."""
    return {key: max(0, value - 2) for key, value in resources.items()}


def eligible_events(after_baseline: dict[str, int]) -> list[tuple[str, str]]:
    return [
        (name, resource) for name, resource in EVENT_CATALOG
        if resource in after_baseline and 0 < after_baseline[resource] <= THRESHOLD
    ]


def sample_transition(resources: dict[str, int], seed: int, next_turn: int) -> dict[str, Any]:
    """Aplica uma transição somente ao snapshot recebido; não altera o argumento."""
    after = baseline_resources(resources)
    eligible = eligible_events(after)
    if not eligible:
        return {
            "resources": after,
            "event": {"kind": "routine_turn", "turn": next_turn,
                      "rule": MODEL_VERSION, "cause": "Nenhum indicador elegível"},
        }
    choice = _draw(seed, next_turn, "event", len(eligible))
    name, resource = eligible[choice]
    # Frequências 25% / 50% / 25%, inteiramente inventadas para ensino.
    lottery = _draw(seed, next_turn, "severity", 100)
    cumulative = 0
    selected = SEVERITIES[-1]
    for level in SEVERITIES:
        cumulative += level[2]
        if lottery < cumulative:
            selected = level
            break
    label, requested_effect, weight = selected
    before = after[resource]
    after[resource] = max(0, before - requested_effect)
    return {
        "resources": after,
        "event": {
            "kind": "scenario_event",
            "turn": next_turn,
            "name": name,
            "resource": resource,
            "effect": before - after[resource],
            "severity": label,
            "cause": f"Indicador fictício {resource} em {before}, dentro do patamar de revisão (<= {THRESHOLD})",
            "rule": MODEL_VERSION,
            "distribution": "leve:25%, moderada:50%, acentuada:25%",
            "candidate_count": len(eligible),
        },
    }


def forecast(resources: dict[str, int], seed: int, turn: int, repetitions: int = 500) -> dict[str, Any]:
    """Experimentação estatística sobre O PRÓXIMO turno; não altera a partida.

    Distribuição entre possíveis sementes simuladas, com incerteza declarada.
    Não é um prognóstico militar nem calcula probabilidades de combate.
    """
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or not 1 <= repetitions <= 2000:
        raise ValueError("Repetições devem estar entre 1 e 2000")
    if turn >= 20:
        raise ValueError("Limite de turnos alcançado")
    next_turn = turn + 1
    categories: Counter[str] = Counter()
    severities: Counter[str] = Counter()
    variations = {key: [] for key in resources}
    for i in range(repetitions):
        # Mistura de sementes estável, separada da evolução da partida.
        sampled_seed = seed + i * 7919
        result = sample_transition(resources, sampled_seed, next_turn)
        event = result["event"]
        categories[event.get("resource", "sem_ocorrencia")] += 1
        severities[event.get("severity", "sem_ocorrencia")] += 1
        for key, value in resources.items():
            variations[key].append(value - result["resources"][key])
    return {
        "model_version": MODEL_VERSION,
        "turn": next_turn,
        "repetitions": repetitions,
        "seed": seed,
        "categories": dict(sorted(categories.items())),
        "severities": dict(sorted(severities.items())),
        "average_variation": {
            key: round(sum(values) / repetitions, 3)
            for key, values in sorted(variations.items())
        },
        "warning": "Frequências e intensidades são hipotéticas. Não representam eficácia ou previsões de combate.",
    }
