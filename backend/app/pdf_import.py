"""Extração documental isolada; não interpreta ordens nem executa anexos."""
import io
import json
import subprocess
import sys

MAX_BYTES = 2_000_000

def extract_pdf(data: bytes) -> dict:
    if len(data) > MAX_BYTES or not data.startswith(b"%PDF-"):
        raise ValueError("Envie um PDF de até 2 MB.")
    try:
        result = subprocess.run([sys.executable, "-m", "backend.app.pdf_import"],
                                input=data, capture_output=True, timeout=10)
    except subprocess.TimeoutExpired:
        raise ValueError("Tempo de extração excedido; use um documento menor.")
    if result.returncode:
        raise ValueError("PDF inválido, protegido, excessivo ou sem texto selecionável. OCR não disponível.")
    return json.loads(result.stdout)

def worker():
    from pypdf import PdfReader
    data = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        return 1
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted or len(reader.pages) > 30:
        return 1
    pages = []
    total = 0
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        total += len(text)
        if total > 60000:
            return 1
        pages.append({"page": i + 1, "text": text})
    if not any(p["text"].strip() for p in pages):
        return 1
    sys.stdout.buffer.write(json.dumps({"pages": pages, "warning": "Extração textual: confira a ordem de leitura no PDF. Nenhuma unidade ou posição foi inferida."}, ensure_ascii=False).encode("utf-8"))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(worker())
    except Exception:
        raise SystemExit(1)
