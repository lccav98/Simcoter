"""Motor didático reproduzível do SIMCOTER (sem parâmetros militares reais)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .probability import sample_transition, forecast
from .access import issue_credentials, fingerprint, verify_fingerprint
from .virtual_staff import create_proposal, coordinate, AGENTS
from .readiness import unit_state, apply_training_variation, READINESS_VERSION, can_participate, advance_turn
from .environment import WEATHER, environment_view, movement_check, ENV_VERSION

INITIAL_RESOURCES = {"suprimentos": 90, "manutencao": 85, "transporte": 88, "saude": 92}
TEACHING_EVENTS = [
    ("Atraso administrativo no recebimento de materiais", "suprimentos", 4),
    ("Indisponibilidade temporária de equipamento de apoio", "manutencao", 5),
    ("Interrupção fictícia de infraestrutura", "transporte", 5),
    ("Demanda adicional de atendimento em exercício", "saude", 3),
]
UNITS = [
    {"id": "azul-1", "party": "azul", "name": "Unidade fictícia Azul 1", "x": 23, "y": 36, "kind": "infantry", "echelon": "battalion", "readiness": 84},
    {"id": "azul-2", "party": "azul", "name": "Unidade fictícia Azul 2", "x": 32, "y": 73, "kind": "logistics", "echelon": "company", "readiness": 65},
    {"id": "vermelha-1", "party": "vermelha", "name": "Unidade fictícia Vermelha 1", "x": 78, "y": 44, "kind": "command", "echelon": "brigade", "readiness": 92},
]
FEATURES = [
    {"id": "area-azul", "name": "Área de responsabilidade Azul", "kind": "area", "status": "proposed"},
    {"id": "ponto-1", "name": "Ponto administrativo P1", "kind": "point", "status": "proposed"},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def roll(seed: int, turn: int) -> int:
    """Índice estável entre 0 e 3; sem depender do estado global de random."""
    payload = f"{seed}:{turn}:simcoter-v1".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big") % len(TEACHING_EVENTS)


class GameStore:
    """Persistência SQLite para protótipo INDIVIDUAL. Sem autenticação ou isolamento multiusuário."""
    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, state TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS access_tokens (session_id TEXT NOT NULL, role TEXT NOT NULL, token_hash TEXT NOT NULL, PRIMARY KEY(session_id, role))")
            db.commit()

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def _save(self, db, state: dict):
        db.execute(
            "INSERT INTO sessions(id, state) VALUES(?, ?) ON CONFLICT(id) DO UPDATE SET state=excluded.state",
            (state["id"], json.dumps(state, ensure_ascii=False)),
        )
        db.commit()

    def _load(self, db, session_id: str) -> dict:
        row = db.execute("SELECT state FROM sessions WHERE id=?", (session_id,)).fetchone()
        if row is None:
            raise KeyError("Partida não encontrada")
        state = json.loads(row[0])
        state["units"] = unit_state(state["units"])
        state.setdefault("weather", "normal")
        return state

    def create(self, title: str = "Exercício Horizonte", seed: int = 2026) -> dict:
        if not -2**31 <= seed < 2**31:
            raise ValueError("A semente deve caber em um inteiro de 32 bits")
        state = {
            "id": str(uuid.uuid4()), "title": title.strip() or "Exercício Horizonte",
            "seed": seed, "turn": 0, "resources": INITIAL_RESOURCES.copy(),
            "units": unit_state(UNITS), "features": [item.copy() for item in FEATURES],
            "reports": [], "events": [], "staff_tasks": [], "weather": "normal", "created_at": utc_now(),
            "scenario": "Território, organizações e parâmetros inteiramente fictícios.",
        }
        with self._lock, self._connect() as db:
            self._save(db, state)
        return state

    def create_with_credentials(self, title: str = "Exercício Horizonte", seed: int = 2026) -> dict:
        """Credenciais são fornecidas uma única vez ao criador da partida."""
        with self._lock:
            state = self.create(title, seed)
            tokens = issue_credentials()
            with self._connect() as db:
                db.executemany(
                    "INSERT INTO access_tokens(session_id, role, token_hash) VALUES(?, ?, ?)",
                    [(state["id"], role, fingerprint(token)) for role, token in tokens.items()],
                )
                db.commit()
        return {"session": state, "credentials": tokens}

    def authenticate(self, session_id: str, token: str) -> str | None:
        if not token or len(token) > 256:
            return None
        with self._lock, self._connect() as db:
            rows = db.execute(
                "SELECT role, token_hash FROM access_tokens WHERE session_id=?", (session_id,)
            ).fetchall()
        for role, hashed in rows:
            if verify_fingerprint(token, hashed):
                return role
        return None

    def get(self, session_id: str) -> dict:
        with self._lock, self._connect() as db:
            return self._load(db, session_id)

    def prepare(self, session_id: str, payload: dict) -> dict:
        from .preparation import review
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            if state["turn"] != 0:
                raise ValueError("Preparação inicial bloqueada após o primeiro turno")
            previous = state.get("preparation", {})
            if payload["revision"] != previous.get("revision", 0):
                raise ValueError("Revisão desatualizada; recarregue a partida")
            record = dict(payload)
            record["revision"] += 1
            record["status"] = "approved" if record.pop("action") == "approve" else "draft"
            record["gaps"] = review(record)
            record["updated_at"] = utc_now()
            if record["status"] == "approved":
                if record["gaps"]:
                    raise ValueError("Resolva as lacunas documentais antes de aprovar")
                state["units"] = unit_state(record["units"])
            state["preparation"] = record
            state.setdefault("preparation_history", []).append(record.copy())
            state["events"].append({"kind": "preparation", "turn": 0,
                                    "revision": record["revision"], "status": record["status"]})
            self._save(db, state)
            return state

    def report(self, session_id: str, source: str, message: str, party: str) -> dict:
        if party not in {"azul", "vermelha", "instrutor"}:
            raise ValueError("Partido inválido")
        source, message = source.strip(), message.strip()
        if not source or not message:
            raise ValueError("Origem e mensagem são obrigatórias")
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            item = {
                "id": str(uuid.uuid4()), "turn": state["turn"], "source": source,
                "party": party, "message": message, "time": utc_now(), "status": "received",
            }
            state["reports"].append(item)
            state["events"].append({"kind": "report", "turn": state["turn"], "ref": item["id"]})
            self._save(db, state)
        return state

    def approve_feature(self, session_id: str, feature_id: str) -> dict:
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            feature = next((f for f in state["features"] if f["id"] == feature_id), None)
            if feature is None:
                raise ValueError("Medida inexistente")
            if feature["status"] != "approved":
                feature["status"] = "approved"
                state["events"].append({"kind": "overlay_approved", "turn": state["turn"], "ref": feature_id})
            self._save(db, state)
        return state

    def set_document_area(self, session_id, area):
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            if state["turn"] != 0:
                raise ValueError("Área documental só pode ser definida no turno zero.")
            state["document_area"] = area
            state["events"].append({"kind":"document_area_confirmed", "turn":0, "area":area})
            self._save(db, state)
        return state

    def queue_order(self, session_id, unit_id, x, y, authorized):
        with self._lock, self._connect() as db:
            state=self._load(db,session_id)
            if state["turn"]>=20:
                raise ValueError("Exercício encerrado")
            if not any(u["id"]==unit_id for u in state["units"]):
                raise ValueError("Unidade inexistente")
            state["orders"]=[o for o in state.get("orders",[]) if o["unit_id"]!=unit_id]
            state["orders"].append({"unit_id":unit_id,"x":x,"y":y,"authorized":authorized})
            self._save(db,state)
            return state

    def clear_orders(self,session_id):
        with self._lock, self._connect() as db:
            state=self._load(db,session_id)
            state["orders"]=[]
            self._save(db,state)
            return state

    def reviewed_turn(self,session_id,token):
        from .turn_cycle import review
        with self._lock, self._connect() as db:
            state=self._load(db,session_id)
            assessment=review(state)
            if assessment["issues"]:
                raise ValueError("; ".join(assessment["issues"]))
            if token!=assessment["token"]:
                raise ValueError("Revisão ausente ou desatualizada. Revise o turno novamente.")
            orders=state.get("orders",[])
            for order in orders:
                unit=next(u for u in state["units"] if u["id"]==order["unit_id"])
                before={"x":unit["x"],"y":unit["y"]}
                unit["x"],unit["y"]=order["x"],order["y"]
                state["events"].append({"kind":"fictitious_move","turn":state["turn"]+1,
                    "unit_id":unit["id"],"before":before,"after":{"x":unit["x"],"y":unit["y"]},
                    "cause":"Ordem fictícia revisada pelo instrutor"})
            turn=state["turn"]+1
            transition=sample_transition(state["resources"],state["seed"],turn)
            state["resources"]=transition["resources"]
            state["units"],events=advance_turn(state["units"],turn)
            state["events"].extend([transition["event"],*events])
            state["events"].append({"kind":"turn_reviewed","turn":turn,"order_count":len(orders),"review_token":token})
            state["turn"]=turn
            state["orders"]=[]
            self._save(db,state)
            return state

    def next_turn(self, session_id: str) -> dict:
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            if state["turn"] >= 20:
                raise ValueError("Limite didático de 20 turnos atingido")
            turn = state["turn"] + 1
            transition = sample_transition(state["resources"], state["seed"], turn)
            state["resources"] = transition["resources"]
            state["turn"] = turn
            state["events"].append(transition["event"])
            state["units"], availability_events = advance_turn(state["units"], turn)
            state["events"].extend(availability_events)
            self._save(db, state)
        return state

    def unit_readiness(self, session_id: str, unit_id: str, change: int) -> dict:
        """Ajuste pedagógico manual por instrutor; não modela engajamentos."""
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            unit = next((u for u in state["units"] if u["id"] == unit_id), None)
            if unit is None:
                raise KeyError("Unidade inexistente")
            before = unit["readiness"]
            updated = apply_training_variation(unit, change)
            unit.update(updated)
            state["events"].append({
                "kind": "readiness_review", "turn": state["turn"],
                "unit_id": unit_id, "before": before,
                "after": updated["readiness"], "rule": READINESS_VERSION,
                "available_for_simulated_actions": can_participate(updated),
                "cause": "Ajuste de prontidão fictícia pelo instrutor",
            })
            if before > 25 and not can_participate(updated):
                state["events"].append({
                    "kind": "unit_unavailable", "turn": state["turn"],
                    "unit_id": unit_id, "rule": READINESS_VERSION,
                    "cause": "Indicador didático atingiu o limite de indisponibilidade",
                })
            self._save(db, state)
        return state

    def validate_unit_action(self, session_id: str, unit_id: str) -> dict:
        """Bloqueio verificável para futuras ações simuladas, sem executá-las."""
        state = self.get(session_id)
        unit = next((u for u in state["units"] if u["id"] == unit_id), None)
        if unit is None:
            raise KeyError("Unidade inexistente")
        available = can_participate(unit)
        return {"unit_id": unit_id, "allowed": available,
                "status": unit["readiness_status"], "readiness": unit["readiness"],
                "rule": READINESS_VERSION,
                "reason": "Disponível para exercício fictício" if available
                  else "Indisponível para novas ações simuladas"}

    def environment(self, session_id: str) -> dict:
        state = self.get(session_id)
        return environment_view(state["weather"])

    def change_weather(self, session_id: str, weather: str) -> dict:
        if weather not in WEATHER:
            raise ValueError("Condição climática inválida")
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            before = state["weather"]
            state["weather"] = weather
            state["events"].append({
                "kind": "weather_changed", "turn": state["turn"],
                "before": before, "after": weather, "rule": ENV_VERSION,
                "cause": "Alteração climática fictícia pelo instrutor",
            })
            self._save(db, state)
        return state

    def unit_movement_check(
        self, session_id: str, unit_id: str, x: int, y: int,
        authorized: bool = False,
    ) -> dict:
        state = self.get(session_id)
        unit = next((u for u in state["units"] if u["id"] == unit_id), None)
        if unit is None:
            raise KeyError("Unidade inexistente")
        return movement_check(unit, x, y, state["weather"], authorized)

    def move_unit(
        self, session_id: str, unit_id: str, x: int, y: int,
        authorized: bool = False,
    ) -> dict:
        """Deslocamento entre coordenadas fictícias, sem cálculo de rota."""
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            if state["turn"] > 0 or state.get("preparation", {}).get("status") == "approved":
                raise ValueError("Preparação encerrada: enfileire o deslocamento e revise o próximo turno.")
            unit = next((u for u in state["units"] if u["id"] == unit_id), None)
            if unit is None:
                raise KeyError("Unidade inexistente")
            check = movement_check(unit, x, y, state["weather"], authorized)
            if not check["allowed"]:
                raise ValueError("; ".join(check["reasons"]))
            previous = {"x": unit["x"], "y": unit["y"]}
            unit["x"], unit["y"] = x, y
            state["events"].append({
                "kind": "fictitious_move", "turn": state["turn"],
                "unit_id": unit_id, "before": previous,
                "after": {"x": x, "y": y},
                "terrain": check["terrain"], "weather": check["weather"],
                "human_review": authorized, "rule": ENV_VERSION,
            })
            self._save(db, state)
        return state

    def staff_assign(self, session_id: str, agent: str) -> dict:
        """Nova tarefa documental para um integrante virtual; sem alterar o cenário."""
        if agent not in AGENTS:
            raise ValueError("Agente inexistente")
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            task = create_proposal(state, agent)
            task.update({"id": str(uuid.uuid4()), "turn": state["turn"],
                         "created_at": utc_now(), "reviewed_at": None})
            state.setdefault("staff_tasks", []).append(task)
            state["events"].append({
                "kind": "staff_task_created", "turn": state["turn"], "ref": task["id"],
                "agent": agent,
            })
            self._save(db, state)
        return coordinate(state)

    def staff_review(self, session_id: str, task_id: str, action: str) -> dict:
        """Apenas a API de instrutor deverá expor esta mudança administrativa."""
        if action not in {"approved", "rejected"}:
            raise ValueError("Decisão inválida")
        with self._lock, self._connect() as db:
            state = self._load(db, session_id)
            task = next((t for t in state.get("staff_tasks", []) if t["id"] == task_id), None)
            if task is None:
                raise KeyError("Tarefa inexistente")
            if task["status"] != "proposed":
                raise ValueError("Tarefa já revisada")
            task["status"] = action
            task["reviewed_at"] = utc_now()
            state["events"].append({
                "kind": "staff_task_reviewed", "turn": state["turn"],
                "ref": task_id, "decision": action,
            })
            self._save(db, state)
        return coordinate(state)

    def staff_summary(self, session_id: str) -> dict:
        return coordinate(self.get(session_id))

    def probability_preview(self, session_id: str, repetitions: int = 500) -> dict:
        state = self.get(session_id)
        return forecast(state["resources"], state["seed"], state["turn"], repetitions)

    def apa(self, session_id: str) -> dict:
        state = self.get(session_id)
        changes = {key: INITIAL_RESOURCES[key] - value for key, value in state["resources"].items()}
        return {
            "session_id": session_id, "turns": state["turn"], "seed": state["seed"],
            "events": [event for event in state["events"] if event["kind"] == "scenario_event"],
            "report_count": len(state["reports"]),
            "approved_features": sum(f["status"] == "approved" for f in state["features"]),
            "resource_variations": changes,
            "weather": state.get("weather", "normal"),
            "environmental_movements": [e for e in state["events"] if e["kind"] in {"fictitious_move", "weather_changed"}],
            "unavailable_units": [e for e in state["events"] if e["kind"] == "unit_unavailable"],
            "unit_readiness": [{ "unit_id": u["id"], "name": u["name"],
               "readiness": u["readiness"], "status": u["readiness_status"] }
               for u in state["units"]],
            "methodology": "Resumo descritivo auditável, sem inferência de vitória, causalidade externa ou eficácia militar real.",
            "recommendations": [
                "Conferir a origem e o momento de recebimento de cada relatório.",
                "Comparar medidas propostas e aprovadas.",
                "Revisar o registro de alterações fictícias de recursos e suas justificativas.",
            ],
        }
