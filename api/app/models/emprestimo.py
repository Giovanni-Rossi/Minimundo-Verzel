from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.situacao import Situacao

if TYPE_CHECKING:
    from app.models.leitor import LeitorModel
    from app.models.livro import LivroModel


class EmprestimoModel(Base):
    """Tabela emprestimos. Na API vira o schema Emprestimo.

    A situação fica na coluna status. O banco exige coerência (CHECK status_coerente):
    ATIVO sem data_devolucao, DEVOLVIDO com data_devolucao. Mude os dois juntos.
    """

    __tablename__ = "emprestimos"
    __table_args__ = (
        CheckConstraint(
            "(status = 'ATIVO' AND data_devolucao IS NULL)"
            " OR (status = 'DEVOLVIDO' AND data_devolucao IS NOT NULL)",
            name="status_coerente",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    livro_id: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    leitor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    # Sem values_callable: grava o nome do item (ATIVO/DEVOLVIDO), como no tipo do banco.
    situacao: Mapped[Situacao] = mapped_column(
        "status", Enum(Situacao, name="status_emprestimo"), default=Situacao.ATIVO
    )
    data_emprestimo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    data_devolucao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    livro: Mapped["LivroModel"] = relationship(back_populates="emprestimos")
    leitor: Mapped["LeitorModel"] = relationship(back_populates="emprestimos")
