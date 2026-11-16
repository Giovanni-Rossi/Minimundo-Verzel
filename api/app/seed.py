from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LeitorModel, PerfilUsuario

LEITORES_INICIAIS = ["Ana", "Bruno", "Carla"]

# Não há login. "!" nunca é o hash de uma senha, então ninguém entra com esses usuários.
SENHA_HASH_SEM_LOGIN = "!"


def semear_leitores(db: Session) -> None:
    """Leitores de exemplo para o banco local (CRIAR_TABELAS=true).

    Só insere quando a tabela está vazia. No Postgres do time de banco, quem popula são eles.
    """
    if db.scalar(select(LeitorModel.id).limit(1)) is not None:
        return
    db.add_all(
        [
            LeitorModel(
                nome=nome,
                email=f"{nome.lower()}@exemplo.com",
                senha_hash=SENHA_HASH_SEM_LOGIN,
                perfil=PerfilUsuario.LEITOR,
            )
            for nome in LEITORES_INICIAIS
        ]
    )
    db.commit()
