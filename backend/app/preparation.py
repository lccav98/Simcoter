"""Preparação documental de cenários exclusivamente fictícios."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Entry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["terreno", "clima", "adversario", "civis"]
    description: str = Field(default="", max_length=2000)
    source: str = Field(default="", max_length=300)
    validity: str = Field(default="", max_length=120)
    certainty: Literal["fato_do_cenario", "hipotese", "lacuna"] = "lacuna"

class UnitPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,60}$")
    name: str = Field(min_length=1, max_length=120)
    party: Literal["azul", "vermelha"]
    parent: str = Field(default="", max_length=60)
    kind: Literal["infantry", "logistics", "command", "engineering", "communications", "medical", "transport"] = "logistics"
    echelon: Literal["company", "battalion", "brigade"] = "company"
    x: int = Field(ge=0, le=100, strict=True)
    y: int = Field(ge=0, le=100, strict=True)
    readiness: int = Field(ge=0, le=100, strict=True)

class Preparation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(default=0, ge=0, strict=True)
    action: Literal["draft", "approve"] = "draft"
    fictional: Literal[True]
    objective: str = Field(default="", max_length=3000)
    situation: str = Field(default="", max_length=3000)
    instructions: str = Field(default="", max_length=3000)
    constraints: str = Field(default="", max_length=3000)
    support: str = Field(default="", max_length=3000)
    coordination: str = Field(default="", max_length=3000)
    units: list[UnitPlan] = Field(min_length=1, max_length=50)
    information: list[Entry] = Field(max_length=40)

    @model_validator(mode="after")
    def hierarchy(self):
        units = {u.id: u for u in self.units}
        if len(units) != len(self.units):
            raise ValueError("Identificadores de unidades duplicados")
        for unit in self.units:
            if not unit.name.strip():
                raise ValueError("Nome de unidade obrigatório")
            seen = {unit.id}
            parent = unit.parent
            while parent:
                if parent not in units or parent in seen:
                    raise ValueError("Subordinação inexistente ou circular")
                if units[parent].party != unit.party:
                    raise ValueError("Subordinação entre partidos não permitida")
                seen.add(parent)
                parent = units[parent].parent
        return self

def review(data):
    gaps = []
    for field, label in [("objective","Objetivo pedagógico"),("situation","Situação"),
                         ("instructions","Instruções"),("constraints","Restrições"),
                         ("support","Apoio"),("coordination","Coordenação")]:
        if not data.get(field, "").strip():
            gaps.append(f"{label}: campo não preenchido")
    for category in ("terreno", "clima", "adversario", "civis"):
        entries = [e for e in data["information"] if e["category"] == category]
        if not entries:
            gaps.append(f"{category}: sem registro")
        for entry in entries:
            if not entry["description"].strip() or not entry["source"].strip() or not entry["validity"].strip():
                gaps.append(f"{category}: descrição, fonte ou validade ausente")
    return gaps
