from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.emprestimo import EmprestimoModel


class LeitorModel(Base):
    """Tabela de leitores. Na API vira o schema Leitor. Os leitores vêm semeados (app/seed.py)."""

    __tablename__ = "leitores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))

    emprestimos: Mapped[list["EmprestimoModel"]] = relationship(back_populates="leitor")
