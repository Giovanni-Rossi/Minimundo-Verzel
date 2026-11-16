from app.schemas.base import SchemaBase


class LivroNovo(SchemaBase):
    """Corpo do POST /livros (BIBL-1).

    As validações do BIBL-1 ficam com quem implementar a história, usando as mensagens do contrato:
    "Título é obrigatório." | "Ano não pode ser no futuro." | "Cópias não podem ser negativas."
    """

    titulo: str
    autor: str
    ano: int
    copias_disponiveis: int


class Livro(LivroNovo):
    id: int


class LivroResumo(SchemaBase):
    """Livro dentro de um Emprestimo."""

    id: int
    titulo: str
