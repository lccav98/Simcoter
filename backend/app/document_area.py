"""Propostas documentais explícitas; não geocodifica nem infere localidades."""
import re
from pydantic import BaseModel, Field

class Page(BaseModel):
    page: int = Field(ge=1, le=30)
    text: str = Field(max_length=60000)

class AreaDocument(BaseModel):
    pages: list[Page] = Field(min_length=1, max_length=30)

def propose(document):
    if sum(len(p.text) for p in document.pages) > 60000:
        raise ValueError("Texto excede 60 mil caracteres.")
    candidates = []
    for page in document.pages:
        for line in page.text.splitlines():
            # Ordem declarada evita confundir latitude/longitude e datum.
            match = re.fullmatch(r"\s*AREA_EXERCICIO_WGS84\s*:\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*", line)
            if not match:
                continue
            west, south, east, north = map(float, match.groups())
            if not (-180 <= west < east <= 180 and -85 <= south < north <= 85):
                continue
            candidates.append({"bounds":[west,south,east,north],"page":page.page,"excerpt":line.strip()})
    return {"candidates":candidates,"warning":"Confirme os limites. Somente AREA_EXERCICIO_WGS84: oeste,sul,leste,norte em graus decimais é reconhecido. Sem OCR, geocodificação de nomes ou inferência de limites."}
