"""API local para demonstração individual do SIMCOTER.

IMPORTANTE: sem autenticação. Não expor a rede pública ou usar dados sensíveis.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .game import GameStore
from .context import analyze_context
from .doctrine import search_catalog

DB_PATH = os.getenv("SIMCOTER_DB", str(Path(__file__).resolve().parents[2] / "data" / "simcoter.sqlite3"))
store = GameStore(DB_PATH)
app = FastAPI(title="SIMCOTER - Protótipo educacional", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class NewSession(BaseModel):
    title: str = Field(default="Exercício Horizonte", max_length=120)
    seed: int = 2026


class NewReport(BaseModel):
    source: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=1000)
    party: str = "azul"


def call(fn, *args):
    try:
        return fn(*args)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "individual", "ai_required": False}


@app.post("/api/sessions")
def create_session(body: NewSession):
    return call(store.create, body.title, body.seed)


@app.get("/api/sessions/{session_id}")
def read_session(session_id: str):
    return call(store.get, session_id)


@app.post("/api/sessions/{session_id}/reports")
def add_report(session_id: str, body: NewReport):
    return call(store.report, session_id, body.source, body.message, body.party)


@app.post("/api/sessions/{session_id}/turns")
def next_turn(session_id: str):
    return call(store.next_turn, session_id)


@app.post("/api/sessions/{session_id}/features/{feature_id}/approve")
def approve_feature(session_id: str, feature_id: str):
    return call(store.approve_feature, session_id, feature_id)


@app.get("/api/sessions/{session_id}/apa")
def get_apa(session_id: str):
    return call(store.apa, session_id)


@app.get("/api/doctrine")
def doctrine_catalog(q: str = ""):
    if len(q) > 160:
        raise HTTPException(status_code=400, detail="Consulta muito longa")
    return {"items": search_catalog(q), "mode": "metadata_only", "verified_citations": False}


@app.get("/api/sessions/{session_id}/context")
def context_problems(session_id: str):
    state = call(store.get, session_id)
    return analyze_context(state)


@app.get("/api/sessions/{session_id}/probability")
def probability_preview(session_id: str, repetitions: int = 500):
    """Prévia estatística abstrata e não mutável do próximo turno."""
    return call(store.probability_preview, session_id, repetitions)
