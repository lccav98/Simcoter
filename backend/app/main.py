"""API experimental com tokens por partida e autorização por partido.

Uso exclusivo em localhost. Tokens não substituem identidades e sessões reais.
"""
from __future__ import annotations

import os
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .game import GameStore
from .access import visible_state
from .context import analyze_context
from .doctrine import search_catalog
from .local_ai import explain
from .virtual_staff import staff_catalog

DB_PATH = os.getenv("SIMCOTER_DB", str(Path(__file__).resolve().parents[2] / "data" / "simcoter.sqlite3"))
store = GameStore(DB_PATH)
app = FastAPI(title="SIMCOTER - Protótipo educacional", version="0.8.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False, allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class NewSession(BaseModel):
    title: str = Field(default="Exercício Horizonte", max_length=120)
    seed: int = 2026


class NewReport(BaseModel):
    source: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=1000)
    # Somente instrutor pode escolher o partido de destino.
    party: str | None = None


def call(fn, *args):
    try:
        return fn(*args)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Recurso não encontrado") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def guard(session_id: str, authorization: str | None, instructor: bool = False) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Credencial obrigatória")
    token = authorization[7:].strip()
    role = store.authenticate(session_id, token)
    if role is None:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if instructor and role != "instrutor":
        raise HTTPException(status_code=403, detail="Ação reservada ao instrutor")
    return role


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "individual_protected", "ai_required": False}


@app.post("/api/sessions")
def create_session(body: NewSession):
    created = call(store.create_with_credentials, body.title, body.seed)
    created["session"] = visible_state(created["session"], "instrutor")
    created["session"]["role"] = "instrutor"
    return created


@app.get("/api/sessions/{session_id}")
def read_session(session_id: str, authorization: str | None = Header(default=None)):
    role = guard(session_id, authorization)
    return visible_state(call(store.get, session_id), role)


@app.post("/api/sessions/{session_id}/reports")
def add_report(session_id: str, body: NewReport, authorization: str | None = Header(default=None)):
    role = guard(session_id, authorization)
    if role != "instrutor" and body.party not in (None, role):
        raise HTTPException(status_code=403, detail="Não é permitido alterar o destinatário")
    destination = (body.party or role)
    return visible_state(call(store.report, session_id, body.source, body.message, destination), role)


@app.post("/api/sessions/{session_id}/turns")
def next_turn(session_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return call(store.next_turn, session_id)


@app.post("/api/sessions/{session_id}/features/{feature_id}/approve")
def approve_feature(session_id: str, feature_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return call(store.approve_feature, session_id, feature_id)


@app.get("/api/sessions/{session_id}/apa")
def get_apa(session_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return call(store.apa, session_id)


@app.get("/api/doctrine")
def doctrine_catalog(q: str = ""):
    if len(q) > 160:
        raise HTTPException(status_code=400, detail="Consulta muito longa")
    return {"items": search_catalog(q), "mode": "metadata_only", "verified_citations": False}


@app.get("/api/sessions/{session_id}/context")
def context_problems(session_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return analyze_context(call(store.get, session_id))


@app.get("/api/sessions/{session_id}/probability")
def probability_preview(
    session_id: str, repetitions: int = 500, authorization: str | None = Header(default=None)
):
    guard(session_id, authorization, instructor=True)
    return call(store.probability_preview, session_id, repetitions)


@app.get("/api/sessions/{session_id}/ai/explanation")
def ai_explanation(session_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return explain(call(store.get, session_id))


class StaffAssignment(BaseModel):
    agent: str = Field(min_length=2, max_length=2)


class StaffReview(BaseModel):
    action: str


@app.get("/api/sessions/{session_id}/staff")
def read_staff(session_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return {"catalog": staff_catalog(), **call(store.staff_summary, session_id)}


@app.post("/api/sessions/{session_id}/staff/tasks")
def assign_staff_task(
    session_id: str, body: StaffAssignment,
    authorization: str | None = Header(default=None),
):
    guard(session_id, authorization, instructor=True)
    return call(store.staff_assign, session_id, body.agent)


@app.post("/api/sessions/{session_id}/staff/tasks/{task_id}/review")
def review_staff_task(
    session_id: str, task_id: str, body: StaffReview,
    authorization: str | None = Header(default=None),
):
    guard(session_id, authorization, instructor=True)
    return call(store.staff_review, session_id, task_id, body.action)


class ReadinessUpdate(BaseModel):
    change: int = Field(ge=-100, le=100)


@app.post("/api/sessions/{session_id}/units/{unit_id}/readiness")
def review_unit_readiness(
    session_id: str, unit_id: str, body: ReadinessUpdate,
    authorization: str | None = Header(default=None),
):
    guard(session_id, authorization, instructor=True)
    return call(store.unit_readiness, session_id, unit_id, body.change)


@app.get("/api/sessions/{session_id}/units/{unit_id}/availability")
def check_unit_availability(
    session_id: str, unit_id: str,
    authorization: str | None = Header(default=None),
):
    role = guard(session_id, authorization)
    state = call(store.get, session_id)
    unit = next((u for u in state["units"] if u["id"] == unit_id), None)
    if unit is None or (role != "instrutor" and unit["party"] != role):
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    return call(store.validate_unit_action, session_id, unit_id)


class WeatherUpdate(BaseModel):
    weather: str


class MovementRequest(BaseModel):
    x: int = Field(ge=0,le=100)
    y: int = Field(ge=0,le=100)
    authorized: bool = False


@app.get("/api/sessions/{session_id}/environment")
def get_environment(session_id: str, authorization: str | None = Header(default=None)):
    guard(session_id, authorization, instructor=True)
    return call(store.environment, session_id)


@app.post("/api/sessions/{session_id}/environment/weather")
def update_weather(
    session_id: str, body: WeatherUpdate,
    authorization: str | None = Header(default=None),
):
    guard(session_id, authorization, instructor=True)
    return call(store.change_weather, session_id, body.weather)


@app.post("/api/sessions/{session_id}/units/{unit_id}/movement/check")
def check_movement(
    session_id: str, unit_id: str, body: MovementRequest,
    authorization: str | None = Header(default=None),
):
    guard(session_id, authorization, instructor=True)
    return call(store.unit_movement_check, session_id, unit_id,
                body.x, body.y, body.authorized)


@app.post("/api/sessions/{session_id}/units/{unit_id}/movement")
def apply_movement(
    session_id: str, unit_id: str, body: MovementRequest,
    authorization: str | None = Header(default=None),
):
    guard(session_id, authorization, instructor=True)
    return call(store.move_unit, session_id, unit_id,
                body.x, body.y, body.authorized)


# Servir o build Vite na mesma origem da API. A montagem só ocorre quando
# o frontend já foi compilado; desenvolvimento continua com Vite na porta 5173.
DIST_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (DIST_DIR / "index.html").is_file():
    if (DIST_DIR / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def index_page():
        return FileResponse(DIST_DIR / "index.html", headers={"Cache-Control": "no-store"})

    @app.get("/{frontend_path:path}", include_in_schema=False)
    def spa_page(frontend_path: str):
        # Não devolver HTML para APIs ou recursos ausentes com extensão.
        if frontend_path == "api" or frontend_path.startswith("api/") or Path(frontend_path).suffix:
            raise HTTPException(status_code=404, detail="Recurso não encontrado")
        return FileResponse(DIST_DIR / "index.html", headers={"Cache-Control": "no-store"})


