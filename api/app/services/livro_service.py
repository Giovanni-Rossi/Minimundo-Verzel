from sqlalchemy.orm import Session

from app.models import LivroModel
from app.schemas import LivroNovo


class LivroService:
    """BIBL-1: cadastro e listagem do acervo."""

    def __init__(self, db: Session):
        self.db = db

    def listar_livros(self) -> list[LivroModel]:
        """GET /livros. Sem livros cadastrados = []."""
        raise NotImplementedError("BIBL-1 listar livros")

    def cadastrar_livro(self, dados: LivroNovo) -> LivroModel:
        """POST /livros.

        400 (RequisicaoInvalida): "Título é obrigatório." | "Ano não pode ser no futuro."
                                  | "Cópias não podem ser negativas."
        """
        raise NotImplementedError("BIBL-1 cadastrar livro")
