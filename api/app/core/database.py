from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_url = settings.url_banco

if _url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
else:
    # O pooler do Neon (PgBouncer) não combina com os prepared statements automáticos do psycopg.
    _connect_args = {"prepare_threshold": None}

# pool_pre_ping testa a conexão antes de usar: o Neon fecha conexões paradas.
engine = create_engine(_url, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todas as tabelas (app/models)."""


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


# Sessão do banco pronta para usar como parâmetro: def funcao(db: DB): ...
DB = Annotated[Session, Depends(get_db)]
