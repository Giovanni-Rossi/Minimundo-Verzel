from pydantic import Field

from app.schemas.base import SchemaBase


class LivroNovo(SchemaBase):
    """Corpo do POST /livros (BIBL-1).

    As regras do BIBL-1 (título vazio, ano no futuro, cópias negativas) ficam no LivroService,
    com as mensagens do contrato. Os max_length só evitam estourar o tamanho das colunas.
    """

    titulo: str = Field(max_length=200)
    autor: str = Field(max_length=150)
    ano: int
    copias_disponiveis: int


class Livro(LivroNovo):
    id: int


class LivroResumo(SchemaBase):
    """Livro dentro de um Emprestimo."""

    id: int
    titulo: str
