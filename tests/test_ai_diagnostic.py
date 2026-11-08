import json
from scripts import check_local_ai


def test_diagnostic_rejects_remote_before_connecting(monkeypatch, capsys):
    monkeypatch.setenv("SIMCOTER_OLLAMA_URL", "http://example.com")
    monkeypatch.setattr(check_local_ai.request, "build_opener",
                        lambda *args: (_ for _ in ()).throw(AssertionError("network forbidden")))
    assert check_local_ai.main() == 1
    assert json.loads(capsys.readouterr().out)["generation_tested"] is False


def test_diagnostic_reports_missing_model_without_generation(monkeypatch, capsys):
    monkeypatch.setenv("SIMCOTER_OLLAMA_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("SIMCOTER_OLLAMA_MODEL", "example:1")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, limit): return b'{"models":[]}'
    class Opener:
        def open(self, url, timeout):
            assert url == "http://127.0.0.1:11434/api/tags"
            assert timeout == 3
            return Response()
    monkeypatch.setattr(check_local_ai.request, "build_opener", lambda *args: Opener())
    assert check_local_ai.main() == 2
    assert json.loads(capsys.readouterr().out)["configured_model_installed"] is False
