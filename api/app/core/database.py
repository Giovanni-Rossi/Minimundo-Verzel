from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todas as tabelas (app/models)."""


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


# Sessão do banco pronta para usar como parâmetro: def funcao(db: DB): ...
DB = Annotated[Session, Depends(get_db)]
