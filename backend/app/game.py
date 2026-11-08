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

INITIAL_RESOURCES = {"suprimentos": 90, "manutencao": 85, "transporte": 88, "saude": 92}
TEACHING_EVENTS = [
    ("Atraso administrativo no recebimento de materiais", "suprimentos", 4),
    ("Indisponibilidade temporária de equipamento de apoio", "manutencao", 5),
    ("Interrupção fictícia de infraestrutura", "transporte", 5),
    ("Demanda adicional de atendimento em exercício", "saude", 3),
]
UNITS = [
    {"id": "azul-1", "party": "azul", "name": "Organização Azul 1", "x": 23, "y": 36},
    {"id": "azul-2", "party": "azul", "name": "Organização Azul 2", "x": 32, "y": 73},
    {"id": "vermelha-1", "party": "vermelha", "name": "Organização Vermelha 1", "x": 78, "y": 44},
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
        return json.loads(row[0])

    def create(self, title: str = "Exercício Horizonte", seed: int = 2026) -> dict:
        if not -2**31 <= seed < 2**31:
            raise ValueError("A semente deve caber em um inteiro de 32 bits")
        state = {
            "id": str(uuid.uuid4()), "title": title.strip() or "Exercício Horizonte",
            "seed": seed, "turn": 0, "resources": INITIAL_RESOURCES.copy(),
            "units": UNITS, "features": [item.copy() for item in FEATURES],
            "reports": [], "events": [], "staff_tasks": [], "created_at": utc_now(),
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
            "methodology": "Resumo descritivo auditável, sem inferência de vitória, causalidade externa ou eficácia militar real.",
            "recommendations": [
                "Conferir a origem e o momento de recebimento de cada relatório.",
                "Comparar medidas propostas e aprovadas.",
                "Revisar o registro de alterações fictícias de recursos e suas justificativas.",
            ],
        }
