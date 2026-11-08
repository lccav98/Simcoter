"""Estado-Maior Virtual: agentes pedagógicos lógicos, sem comando autônomo.

O coordenador atribui revisões de documentos a E1/E2/E3/E4 e agrega
propostas fundamentadas no estado fictício da partida. A integração
Paperclip é um *contrato* opcional, não um serviço instalado.
"""
from __future__ import annotations

from hashlib import sha256
import json

STAFF_VERSION = "emv-v1"
AGENTS = {
    "E1": {"title": "Pessoal", "responsibility": "Conferência de registros administrativos fictícios"},
    "E2": {"title": "Informações", "responsibility": "Conferência de fontes e metadados de relatórios"},
    "E3": {"title": "Planejamento", "responsibility": "Coerência documental e aprovação de medidas"},
    "E4": {"title": "Logística", "responsibility": "Conferência de indicadores logísticos fictícios"},
}
ADAPTERS = ("builtin", "paperclip")


def staff_catalog() -> dict:
    return {"version": STAFF_VERSION, "agents": AGENTS, "default_adapter": "builtin",
            "optional_adapter": "paperclip", "paperclip_installed": False}


def _evidence_snapshot(state: dict, agent: str) -> dict:
    """Cada função recebe apenas dados necessários à tarefa didática."""
    if agent == "E1":
        return {"unit_count": len(state["units"]), "turn": state["turn"]}
    if agent == "E2":
        # Não enviar texto dos relatórios e nem identificar conteúdo reservado.
        return {"report_count": len(state["reports"]), "sources_present":
                sorted(set(r["source"] for r in state["reports"])), "turn": state["turn"]}
    if agent == "E3":
        return {"features": [{"id": f["id"], "status": f["status"]} for f in state["features"]],
                "turn": state["turn"]}
    if agent == "E4":
        return {"resources": dict(state["resources"]), "turn": state["turn"]}
    raise ValueError("Agente inexistente")


def create_proposal(state: dict, agent: str) -> dict:
    """Gera somente uma proposta documental; sem alteração de recursos/turno."""
    if agent not in AGENTS:
        raise ValueError("Agente inexistente")
    evidence = _evidence_snapshot(state, agent)
    if agent == "E1":
        title = "Conferência administrativa de pessoal"
        note = f"Há {evidence['unit_count']} organizações fictícias cadastradas; conferir a atualização do quadro."
    elif agent == "E2":
        title = "Conferência de fontes recebidas"
        note = f"Há {evidence['report_count']} relatórios fictícios; revisar origem, cronologia e possíveis lacunas."
    elif agent == "E3":
        pending = sum(f["status"] == "proposed" for f in evidence["features"])
        title = "Verificação de documentos e medidas"
        note = f"Há {pending} medidas pendentes; conferir os registros e aprovações pertinentes."
    else:
        low = [k for k, v in evidence["resources"].items() if v <= 75]
        title = "Análise administrativa de indicadores logísticos"
        note = ("Revisar documentação dos indicadores: " + ", ".join(low)
                if low else "Conferir as previsões e a consistência dos indicadores fictícios.")
    evidence_json = json.dumps(evidence, ensure_ascii=False, sort_keys=True)
    digest = sha256((STAFF_VERSION + "|" + agent + "|" + evidence_json).encode()).hexdigest()
    return {
        "agent": agent, "agent_title": AGENTS[agent]["title"],
        "title": title, "summary": note, "evidence": evidence,
        "evidence_hash": digest, "rule": STAFF_VERSION,
        "status": "proposed", "scope": "educational_document_review",
        "warning": "A proposta é didática; não constitui decisão operacional.",
    }


def coordinate(state: dict) -> dict:
    """Chefe de EM lógico consolida tarefas; não concede aprovações."""
    tasks = state.get("staff_tasks", [])
    return {
        "turn": state["turn"], "adapter": "builtin", "version": STAFF_VERSION,
        "tasks": tasks,
        "summary": {
            "proposed": sum(t["status"] == "proposed" for t in tasks),
            "approved": sum(t["status"] == "approved" for t in tasks),
            "rejected": sum(t["status"] == "rejected" for t in tasks),
        },
        "decisions_require_human_approval": True,
    }


class StaffAdapter:
    """Interface mínima para um adaptador externo futuro.

    Paperclip só poderá produzir artefatos sujeitos aos mesmos validadores
    e nunca receber credenciais de outros partidos ou alterar o estado.
    """

    name = "builtin"

    def propose(self, state: dict, agent: str) -> dict:
        return create_proposal(state, agent)


class PaperclipAdapter(StaffAdapter):
    name = "paperclip"

    def propose(self, state: dict, agent: str) -> dict:
        raise RuntimeError("Adaptador Paperclip não instalado: usar backend builtin")
