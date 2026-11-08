import json

import pytest

from backend.app import local_ai
from backend.app.game import GameStore


@pytest.fixture
def scenario(tmp_path):
    store = GameStore(tmp_path / "session.sqlite3")
    return store.next_turn(store.create(seed=5)["id"])


def test_disabled_by_default(monkeypatch, scenario):
    monkeypatch.delenv("SIMCOTER_AI_ENABLED", raising=False)
    output = local_ai.explain(scenario)
    assert output["mode"] == "rules_fallback"
    assert output["available"] is False
    assert "context_hash" in output


def test_evidence_omits_report_text(tmp_path):
    store = GameStore(tmp_path / "no_leak.sqlite3")
    state = store.create()
    state = store.report(state["id"], "E4", "NÃO ENVIAR ESTE TEXTO", "azul")
    serialized = json.dumps(local_ai.evidence_snapshot(state), ensure_ascii=False)
    assert "NÃO ENVIAR" not in serialized
    assert '"report_count"' in serialized


@pytest.mark.parametrize("url", [
    "https://127.0.0.1:11434", "http://example.org",
    "http://127.0.0.2:11434", "http://localhost:11434/attack",
    "http://user:pass@localhost:11434",
])
def test_rejects_nonlocal_configuration(url, monkeypatch):
    monkeypatch.setenv("SIMCOTER_OLLAMA_URL", url)
    with pytest.raises(ValueError):
        local_ai._local_url()


def test_rejects_invented_evidence():
    with pytest.raises(ValueError):
        local_ai._validate(
            {"summary": "teste", "findings": [
                {"evidence_id": "não-existe", "explanation": "invenção"}
            ], "uncertainties": []}, {"indicator:saude"}
        )


def test_ollama_with_fake_local_response(monkeypatch, scenario):
    monkeypatch.setenv("SIMCOTER_AI_ENABLED", "true")
    monkeypatch.setenv("SIMCOTER_OLLAMA_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("SIMCOTER_OLLAMA_MODEL", "local-test:1")
    evidence = local_ai.evidence_snapshot(scenario)["evidence"][0]["id"]

    class FakeResponse:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None
        def read(self, size):
            answer = {"summary": "Indicadores fictícios revisados.", "findings": [
                {"evidence_id": evidence, "explanation": "Conferir o dado registrado."}
            ], "uncertainties": ["Modelo pedagógico."]}
            return json.dumps({"response": json.dumps(answer)}).encode()

    class FakeOpener:
        def open(self, req, timeout):
            assert req.full_url == "http://127.0.0.1:11434/api/generate"
            assert json.loads(req.data)["think"] is False
            assert timeout == 20
            return FakeResponse()

    monkeypatch.setattr(local_ai.request, "build_opener", lambda *handlers: FakeOpener())
    result = local_ai.explain(scenario)
    assert result["available"] is True
    assert result["findings"][0]["evidence_id"] == evidence


def test_bad_ollama_output_falls_back(monkeypatch, scenario):
    monkeypatch.setenv("SIMCOTER_AI_ENABLED", "true")

    class BadResponse:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None
        def read(self, size):
            return b'{"response": "invalid output"}'

    monkeypatch.setattr(
        local_ai.request, "build_opener",
        lambda *handlers: type("Opener", (), {"open": lambda self, *a, **k: BadResponse()})()
    )
    assert local_ai.explain(scenario)["mode"] == "rules_fallback"

def test_local_request_explicitly_disables_system_proxy(monkeypatch, scenario):
    monkeypatch.setenv("SIMCOTER_AI_ENABLED", "true")
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.invalid:8080")
    inspected = []
    def build(*handlers):
        proxy = next(h for h in handlers if isinstance(h, local_ai.request.ProxyHandler))
        assert proxy.proxies == {}
        assert local_ai._NoRedirect in handlers
        inspected.append(True)
        class Offline:
            def open(self, *args, **kwargs):
                raise OSError("local service unavailable")
        return Offline()
    monkeypatch.setattr(local_ai.request, "build_opener", build)
    assert local_ai.explain(scenario)["mode"] == "rules_fallback"
    assert inspected == [True]
