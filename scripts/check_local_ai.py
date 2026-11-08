"""Diagnóstico local sem gerar texto, enviar partida ou baixar modelos."""
from pathlib import Path
import json
import sys
from urllib import request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.local_ai import _local_url, _model, _NoRedirect, enabled


def main():
    try:
        origin, model = _local_url(), _model()
        opener = request.build_opener(request.ProxyHandler({}), _NoRedirect)
        with opener.open(origin + "/api/tags", timeout=3) as response:
            raw = response.read(128001)
            if len(raw) > 128000:
                raise ValueError("Resposta excessiva")
        models = json.loads(raw).get("models", [])
        installed = any(item.get("name") == model for item in models)
        print(json.dumps({"service": "available", "enabled": enabled(),
                          "configured_model_installed": installed}, ensure_ascii=False))
        return 0 if installed else 2
    except (OSError, ValueError, TypeError, AttributeError):
        print('{"service":"unavailable_or_invalid","generation_tested":false}')
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
