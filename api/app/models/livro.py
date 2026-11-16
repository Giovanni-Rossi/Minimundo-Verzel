from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.emprestimo import EmprestimoModel


class LivroModel(Base):
    """Tabela de livros. Na API vira o schema Livro."""

    __tablename__ = "livros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255))
    autor: Mapped[str] = mapped_column(String(255))
    ano: Mapped[int]
    copias_disponiveis: Mapped[int]

    emprestimos: Mapped[list["EmprestimoModel"]] = relationship(back_populates="livro")
