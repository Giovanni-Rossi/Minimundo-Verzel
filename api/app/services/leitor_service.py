from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LeitorModel, PerfilUsuario


class LeitorService:
    """Leitores. Não há cadastro pela API: eles vêm prontos no banco."""

    def __init__(self, db: Session):
        self.db = db

    def listar_leitores(self) -> list[LeitorModel]:
        """GET /leitores. Só usuários com perfil leitor; bibliotecários ficam de fora."""
        consulta = (
            select(LeitorModel)
            .where(LeitorModel.perfil == PerfilUsuario.LEITOR)
            .order_by(LeitorModel.id)
        )
        return list(self.db.scalars(consulta))
