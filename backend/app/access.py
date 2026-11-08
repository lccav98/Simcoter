"""Controle experimental de acesso por credenciais de partida.

Tokens aleatórios são exibidos uma vez e persistidos apenas como SHA-256.
Não substitui autenticação de usuários nem autoriza operação em LAN pública.
"""
from __future__ import annotations

from hashlib import sha256
import hmac
import secrets

ROLES = ("instrutor", "azul", "vermelha")


def issue_credentials() -> dict[str, str]:
    return {role: secrets.token_urlsafe(32) for role in ROLES}


def fingerprint(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def verify_fingerprint(token: str, expected: str) -> bool:
    if not token or len(token) > 256:
        return False
    return hmac.compare_digest(fingerprint(token), expected)


def visible_state(state: dict, role: str) -> dict:
    """Lista positiva: campos não previstos jamais são enviados a um partido."""
    if role not in ROLES:
        raise ValueError("Papel inválido")
    if role == "instrutor":
        return {**state, "role": "instrutor"}
    return {
        "id": state["id"], "title": state["title"], "turn": state["turn"],
        "scenario": "Exercício fictício com informações limitadas ao partido.",
        "resources": {},
        "units": [u for u in state["units"] if u["party"] == role],
        "features": [f for f in state["features"] if f.get("party") == role],
        "reports": [r for r in state["reports"] if r["party"] == role],
        # O histórico global não é liberado para evitar inferências indiretas.
        "events": [],
        "role": role,
    }
