"""Assessoria didática opcional com Ollama local.

Não decide resultados, não emite ordens e não altera o estado da partida.
Sem rede pública: apenas 127.0.0.1 e localhost. A API está desabilitada
por padrão enquanto não houver autenticação e controle por partido.
"""
from __future__ import annotations

import ipaddress
import json
import os
from urllib import request, error
from urllib.parse import urlsplit

from .context import analyze_context

SUPPORTED_EVIDENCE = {"indicator", "event", "overlay", "report_count"}
AI_SYSTEM = (
    "Você é um tutor pedagógico para um exercício inteiramente fictício. "
    "Use apenas as evidências estruturadas fornecidas. Não elabore instruções "
    "de ataque, seleção de alvos, otimização de engajamentos, manipulação de "
    "públicos ou ações cibernéticas ofensivas. Não atribua frases a manuais "
    "doutrinários que não foram fornecidos. Produza JSON válido com as chaves "
    "summary, findings e uncertainties. Os achados devem conter evidence_id "
    "existente no contexto e explanation. Sem evidência, registre incerteza."
)
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "evidence_id": {"type": "string"},
                    "explanation": {"type": "string"},
                },
                "required": ["evidence_id", "explanation"],
                "additionalProperties": False,
            },
        },
        "uncertainties": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "findings", "uncertainties"],
    "additionalProperties": False,
}


def enabled() -> bool:
    return os.getenv("SIMCOTER_AI_ENABLED", "false").lower() == "true"


def _local_url() -> str:
    raw = os.getenv("SIMCOTER_OLLAMA_URL", "http://127.0.0.1:11434")
    parsed = urlsplit(raw)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise ValueError("A IA exige URL HTTP em localhost/127.0.0.1")
    if parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("A URL do Ollama deve conter apenas a origem local")
    if parsed.port is not None and not (1 <= parsed.port <= 65535):
        raise ValueError("Porta de Ollama inválida")
    return raw.rstrip("/")


def _model() -> str:
    name = os.getenv("SIMCOTER_OLLAMA_MODEL", "qwen3:4b").strip()
    if not name or len(name) > 100 or not all(c.isalnum() or c in "-_./:" for c in name):
        raise ValueError("Nome do modelo não permitido")
    return name


def evidence_snapshot(state: dict) -> dict:
    """Evita transmitir textos livres de relatórios e dados não autorizados."""
    evidence: list[dict] = []
    for key, value in sorted(state["resources"].items()):
        evidence.append({"id": f"indicator:{key}", "kind": "indicator", "value": value})
    for index, event in enumerate(state["events"]):
        if event["kind"] in {"scenario_event", "routine_turn"}:
            evidence.append({
                "id": f"event:{index}", "kind": "event", "turn": event["turn"],
                "name": event.get("name", "Turno rotineiro"),
                "rule": event.get("rule"), "effect": event.get("effect", 0),
                "resource": event.get("resource"),
            })
    for feature in state["features"]:
        evidence.append({
            "id": f"overlay:{feature['id']}", "kind": "overlay",
            "status": feature["status"],
        })
    evidence.append({
        "id": "report_count", "kind": "report_count", "value": len(state["reports"]),
    })
    # Snapshot limitado, para evitar prompts ilimitados.
    evidence = evidence[-60:]
    return {
        "turn": state["turn"],
        "seed": state["seed"],
        "context_hash": analyze_context(state)["context_hash"],
        "evidence": evidence,
    }


def _fallback(snapshot: dict, reason: str) -> dict:
    return {
        "mode": "rules_fallback",
        "available": False,
        "model": None,
        "context_hash": snapshot["context_hash"],
        "summary": "A análise narrativa por IA não está disponível. Os dados da partida permanecem intactos.",
        "findings": [],
        "uncertainties": [reason],
        "evidence": snapshot["evidence"],
    }


def _validate(response: object, valid_ids: set[str]) -> dict:
    if not isinstance(response, dict) or set(response) != {"summary", "findings", "uncertainties"}:
        raise ValueError("Formato de resposta inválido")
    summary, findings, uncertainties = (response[k] for k in ("summary", "findings", "uncertainties"))
    if not isinstance(summary, str) or len(summary) > 1500:
        raise ValueError("Resumo inválido")
    if not isinstance(findings, list) or len(findings) > 12:
        raise ValueError("Quantidade de achados inválida")
    if not isinstance(uncertainties, list) or len(uncertainties) > 12 or not all(
        isinstance(x, str) and len(x) <= 500 for x in uncertainties
    ):
        raise ValueError("Incertezas inválidas")
    for item in findings:
        if not isinstance(item, dict) or set(item) != {"evidence_id", "explanation"}:
            raise ValueError("Achado inválido")
        if item["evidence_id"] not in valid_ids or not isinstance(item["explanation"], str) or len(item["explanation"]) > 900:
            raise ValueError("Referência de evidência inválida")
    return response


def explain(state: dict) -> dict:
    snapshot = evidence_snapshot(state)
    if not enabled():
        return _fallback(snapshot, "Integração Ollama desativada por configuração.")
    try:
        url = _local_url() + "/api/generate"
        model = _model()
        payload = {
            "model": model, "system": AI_SYSTEM,
            "prompt": "Explique apenas este exercício educativo e responda no esquema JSON fornecido:\n"
                      + json.dumps(snapshot, ensure_ascii=False),
            "stream": False, "format": OUTPUT_SCHEMA,
            "options": {"temperature": 0, "num_predict": 450},
        }
        req = request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        # Impede redirecionamento para rede externa.
        opener = request.build_opener(_NoRedirect)
        with opener.open(req, timeout=20) as response:
            if response.status != 200:
                raise ValueError("Resposta HTTP não permitida")
            raw = response.read(128_001)
            if len(raw) > 128_000:
                raise ValueError("Resposta excessivamente longa")
        envelope = json.loads(raw)
        parsed = json.loads(envelope["response"])
        answer = _validate(parsed, {item["id"] for item in snapshot["evidence"]})
    except (ValueError, TypeError, KeyError, OSError, TimeoutError, json.JSONDecodeError, error.URLError) as exc:
        return _fallback(snapshot, f"Resposta da IA indisponível ou inválida ({type(exc).__name__}).")
    return {
        "mode": "ollama_local", "available": True, "model": model,
        "context_hash": snapshot["context_hash"], **answer,
        "evidence": snapshot["evidence"],
        "warning": "Texto gerado por IA não equivale a conclusão factual independente; confira os registros.",
    }


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Redirecionamento de IA proibido")
