"""Testes de isolamento e integridade de tokens do protótipo."""
from backend.app.access import fingerprint, issue_credentials, verify_fingerprint, visible_state
from backend.app.game import GameStore


def test_tokens_are_distinct_random_secrets():
    creds = issue_credentials()
    assert set(creds) == {"instrutor", "azul", "vermelha"}
    assert len(set(creds.values())) == 3
    for token in creds.values():
        assert len(token) >= 40
        assert verify_fingerprint(token, fingerprint(token))
        assert not verify_fingerprint("outro-token", fingerprint(token))


def test_only_hashes_are_persisted(tmp_path):
    store = GameStore(tmp_path / "auth.sqlite3")
    created = store.create_with_credentials()
    sid, creds = created["session"]["id"], created["credentials"]
    for role, token in creds.items():
        assert store.authenticate(sid, token) == role
    assert store.authenticate(sid, "falso") is None
    with store._connect() as db:
        rows = db.execute("SELECT token_hash FROM access_tokens WHERE session_id=?", (sid,)).fetchall()
    stored = [item[0] for item in rows]
    assert len(stored) == 3
    assert all(token not in stored for token in creds.values())
    assert all(len(item) == 64 for item in stored)


def test_visible_state_does_not_leak_other_party(tmp_path):
    store = GameStore(tmp_path / "filtered.sqlite3")
    sid = store.create_with_credentials()["session"]["id"]
    store.report(sid, "E2", "SEGREDO AZUL", "azul")
    store.report(sid, "E2", "SEGREDO VERMELHO", "vermelha")
    state = store.get(sid)
    blue = visible_state(state, "azul")
    red = visible_state(state, "vermelha")
    assert "SEGREDO VERMELHO" not in str(blue)
    assert "SEGREDO AZUL" not in str(red)
    assert blue["role"] == "azul"
    assert red["role"] == "vermelha"
    assert "seed" not in blue and "seed" not in red
    assert blue["events"] == [] and red["events"] == []
    assert len(visible_state(state, "instrutor")["reports"]) == 2
