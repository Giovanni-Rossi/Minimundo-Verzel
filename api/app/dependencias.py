"""Entrega cada service já ligado ao banco para as rotas: def rota(servico: LivroServiceDep)."""

from typing import Annotated

from fastapi import Depends

from app.core.database import DB
from app.services import EmprestimoService, LeitorService, LivroService, RelatorioService


def _livro_service(db: DB) -> LivroService:
    return LivroService(db)


def _leitor_service(db: DB) -> LeitorService:
    return LeitorService(db)


def _emprestimo_service(db: DB) -> EmprestimoService:
    return EmprestimoService(db)


def _relatorio_service(db: DB) -> RelatorioService:
    return RelatorioService(db)


LivroServiceDep = Annotated[LivroService, Depends(_livro_service)]
LeitorServiceDep = Annotated[LeitorService, Depends(_leitor_service)]
EmprestimoServiceDep = Annotated[EmprestimoService, Depends(_emprestimo_service)]
RelatorioServiceDep = Annotated[RelatorioService, Depends(_relatorio_service)]
