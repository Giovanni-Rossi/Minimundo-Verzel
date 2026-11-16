from sqlalchemy.orm import Session

from app.models import LeitorModel


class LeitorService:
    """Leitores. Não há cadastro pela API: eles vêm semeados no banco (app/seed.py)."""

    def __init__(self, db: Session):
        self.db = db

    def listar_leitores(self) -> list[LeitorModel]:
        """GET /leitores."""
        raise NotImplementedError("listar leitores")
