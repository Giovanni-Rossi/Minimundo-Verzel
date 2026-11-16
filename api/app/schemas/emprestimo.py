from dataclasses import dataclass
from datetime import date, datetime

from pydantic import Field

from app.models.situacao import Situacao
from app.schemas.base import SchemaBase
from app.schemas.leitor import Leitor
from app.schemas.livro import LivroResumo


class EmprestimoNovo(SchemaBase):
    """Corpo do POST /emprestimos (BIBL-2). No JSON: livroId e leitorId."""

    livro_id: int = Field(ge=1)
    leitor_id: int = Field(ge=1)


class Emprestimo(SchemaBase):
    id: int
    livro: LivroResumo
    leitor: Leitor
    data_emprestimo: datetime
    data_devolucao: datetime | None
    situacao: Situacao


@dataclass
class FiltroRelatorio:
    """Filtros do relatório (BIBL-4) e do CSV (BIBL-5). Todos opcionais e combináveis.

    Na URL: ?leitorId=1&inicio=2026-11-01&fim=2026-11-30&situacao=ativo ("fim" é inclusivo).
    """

    leitor_id: int | None = None
    inicio: date | None = None
    fim: date | None = None
    situacao: Situacao | None = None
