import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registra as tabelas no Base.metadata)
from app.core.database import Base, get_db
from app.main import app

engine_teste = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SessaoTeste = sessionmaker(bind=engine_teste, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db():
    """Banco em memória, criado vazio a cada teste."""
    Base.metadata.create_all(engine_teste)
    with SessaoTeste() as sessao:
        yield sessao
    Base.metadata.drop_all(engine_teste)


@pytest.fixture
def client(db):
    """Cliente HTTP usando o banco de teste. Não roda o seed: cada teste cria os dados que precisa."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
