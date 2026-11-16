from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.emprestimo import EmprestimoModel


class LivroModel(Base):
    """Tabela livros. Na API vira o schema Livro."""

    __tablename__ = "livros"
    __table_args__ = (
        CheckConstraint("copias_disponiveis >= 0", name="livros_copias_disponiveis_check"),
        CheckConstraint("trim(titulo) <> ''", name="livros_titulo_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    autor: Mapped[str] = mapped_column(String(150))
    ano: Mapped[int] = mapped_column("ano_publicacao", SmallInteger)
    copias_disponiveis: Mapped[int]
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    emprestimos: Mapped[list["EmprestimoModel"]] = relationship(back_populates="livro")
