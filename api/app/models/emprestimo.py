from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.situacao import Situacao

if TYPE_CHECKING:
    from app.models.leitor import LeitorModel
    from app.models.livro import LivroModel


class EmprestimoModel(Base):
    """Tabela de empréstimos. Na API vira o schema Emprestimo."""

    __tablename__ = "emprestimos"

    id: Mapped[int] = mapped_column(primary_key=True)
    livro_id: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    leitor_id: Mapped[int] = mapped_column(ForeignKey("leitores.id"))
    data_emprestimo: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    data_devolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    situacao: Mapped[Situacao] = mapped_column(
        Enum(Situacao, name="situacao", values_callable=lambda enum: [item.value for item in enum]),
        default=Situacao.ATIVO,
    )

    livro: Mapped["LivroModel"] = relationship(back_populates="emprestimos")
    leitor: Mapped["LeitorModel"] = relationship(back_populates="emprestimos")
