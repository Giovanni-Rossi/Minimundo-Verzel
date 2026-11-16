from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LeitorModel

LEITORES_INICIAIS = ["Ana", "Bruno", "Carla"]


def semear_leitores(db: Session) -> None:
    """O contrato não tem cadastro de leitor, então eles já vêm no banco.

    Só insere quando a tabela está vazia, então pode rodar a cada vez que a API sobe.
    """
    if db.scalar(select(LeitorModel.id).limit(1)) is not None:
        return
    db.add_all([LeitorModel(nome=nome) for nome in LEITORES_INICIAIS])
    db.commit()
