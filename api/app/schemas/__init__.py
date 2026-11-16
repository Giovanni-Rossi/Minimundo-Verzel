"""Schemas da API (JSON de entrada e saída).

Os nomes das classes são os mesmos de components.schemas no contrato openapi-biblioteca.yaml,
porque o FastAPI usa o nome da classe na documentação gerada em /docs.
"""

from app.schemas.emprestimo import Emprestimo, EmprestimoNovo, FiltroRelatorio
from app.schemas.erro import Erro
from app.schemas.leitor import Leitor
from app.schemas.livro import Livro, LivroNovo, LivroResumo
from app.schemas.ranking import ItemRanking

__all__ = [
    "Emprestimo",
    "EmprestimoNovo",
    "Erro",
    "FiltroRelatorio",
    "ItemRanking",
    "Leitor",
    "Livro",
    "LivroNovo",
    "LivroResumo",
]
