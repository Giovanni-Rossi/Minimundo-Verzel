from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.erros import RequisicaoInvalida
from app.models import LivroModel
from app.schemas import LivroNovo


class LivroService:
    """BIBL-1: cadastro e listagem do acervo."""

    def __init__(self, db: Session):
        self.db = db

    def listar_livros(self) -> list[LivroModel]:
        """GET /livros. Na ordem de cadastro. Sem livros cadastrados = []."""
        return list(self.db.scalars(select(LivroModel).order_by(LivroModel.id)))

    def cadastrar_livro(self, dados: LivroNovo) -> LivroModel:
        """POST /livros.

        400 (RequisicaoInvalida): "Título é obrigatório." | "Ano não pode ser no futuro."
                                  | "Cópias não podem ser negativas."
        """
        titulo = dados.titulo.strip()
        if not titulo:
            raise RequisicaoInvalida("Título é obrigatório.")
        if dados.ano > date.today().year:
            raise RequisicaoInvalida("Ano não pode ser no futuro.")
        if dados.copias_disponiveis < 0:
            raise RequisicaoInvalida("Cópias não podem ser negativas.")

        livro = LivroModel(
            titulo=titulo,
            autor=dados.autor.strip(),
            ano=dados.ano,
            copias_disponiveis=dados.copias_disponiveis,
        )
        self.db.add(livro)
        self.db.commit()
        return livro
