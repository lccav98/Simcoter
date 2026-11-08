"""Catálogo offline de REFERÊNCIAS para ensino. Não contém textos de manuais.

A inclusão no catálogo não valida edição/vigência/direitos de redistribuição.
Os títulos e identificadores devem passar por curadoria antes de uso institucional.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import re
import unicodedata


@dataclass(frozen=True)
class DoctrineRecord:
    code: str
    title: str
    category: str
    publisher: str
    edition_status: str
    verification: str
    reference_url: str


RECORDS = (
    DoctrineRecord(
        "EB70-MC-10.211", "Processo de Planejamento e Condução das Operações Terrestres",
        "planejamento", "Exército Brasileiro", "Edição a confirmar na fonte primária",
        "Pendente de curadoria documental", "https://www.eb.mil.br/"
    ),
    DoctrineRecord(
        "EB70-MC-10.238", "Logística Militar Terrestre",
        "logística", "Exército Brasileiro", "Edição a confirmar na fonte primária",
        "Pendente de curadoria documental", "https://www.eb.mil.br/"
    ),
    DoctrineRecord(
        "CE 5.80", "Dados Médios de Planejamento Escolar (DAMEPLAN)",
        "ensino", "Exército Brasileiro", "Edição e vigência a conferir na fonte primária",
        "Pendente de curadoria documental", "https://www.eb.mil.br/"
    ),
    DoctrineRecord(
        "EB70-MC-10.213", "Operações de Informação",
        "informação", "Exército Brasileiro", "Edição a confirmar na fonte primária",
        "Pendente de curadoria documental", "https://www.eb.mil.br/"
    ),
    DoctrineRecord(
        "MD30-M-01", "Doutrina de Operações Conjuntas",
        "conjunta", "Ministério da Defesa", "Volume e edição a confirmar",
        "Pendente de curadoria documental",
        "https://www.gov.br/defesa/pt-br/assuntos/estado-maior-conjunto-das-forcas-armadas/doutrina-militar"
    ),
)


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in value if not unicodedata.combining(char))


def search_catalog(query: str = "") -> list[dict]:
    """Busca local literal nos metadados. NÃO gera citações ao conteúdo dos manuais."""
    q = normalized(query.strip())
    terms = re.findall(r"\w+", q)
    output = []
    for item in RECORDS:
        fields = normalized(" ".join([item.code, item.title, item.category, item.publisher]))
        if all(term in fields for term in terms):
            output.append(asdict(item))
    return output
