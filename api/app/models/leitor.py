from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.perfil import PerfilUsuario

if TYPE_CHECKING:
    from app.models.emprestimo import EmprestimoModel


class LeitorModel(Base):
    """Tabela usuarios. Na API vira o schema Leitor.

    A tabela guarda leitores e bibliotecários. Para a API, leitor é o usuário com perfil LEITOR.
    email e senha_hash existem no banco, mas a API não usa (não há login).
    """

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(
            PerfilUsuario,
            name="perfil_usuario",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=PerfilUsuario.LEITOR,
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    emprestimos: Mapped[list["EmprestimoModel"]] = relationship(back_populates="leitor")
