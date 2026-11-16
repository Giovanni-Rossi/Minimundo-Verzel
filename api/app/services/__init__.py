"""Regras de negócio. Cada história mexe só no service dela; as rotas já estão ligadas."""

from app.services.emprestimo_service import EmprestimoService
from app.services.leitor_service import LeitorService
from app.services.livro_service import LivroService
from app.services.relatorio_service import RelatorioService

__all__ = ["EmprestimoService", "LeitorService", "LivroService", "RelatorioService"]
