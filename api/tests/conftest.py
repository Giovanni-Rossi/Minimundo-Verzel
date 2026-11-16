from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registra as tabelas no Base.metadata)
from app.core.database import Base, get_db
from app.main import app
from app.models import EmprestimoModel, LeitorModel, LivroModel, Situacao

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


class CriadorDeDados:
    """Insere dados direto no banco de teste, sem depender das rotas de outras histórias."""

    def __init__(self, db: Session):
        self.db = db

    def livro(self, titulo: str, copias: int = 3) -> LivroModel:
        livro = LivroModel(titulo=titulo, autor="Autor", ano=2000, copias_disponiveis=copias)
        return self._salvar(livro)

    def leitor(self, nome: str) -> LeitorModel:
        return self._salvar(LeitorModel(nome=nome))

    def emprestimo(
        self,
        livro: LivroModel,
        leitor: LeitorModel,
        em: datetime,
        devolvido_em: datetime | None = None,
    ) -> EmprestimoModel:
        emprestimo = EmprestimoModel(
            livro_id=livro.id,
            leitor_id=leitor.id,
            data_emprestimo=em,
            data_devolucao=devolvido_em,
            situacao=Situacao.DEVOLVIDO if devolvido_em else Situacao.ATIVO,
        )
        return self._salvar(emprestimo)

    def _salvar(self, objeto):
        self.db.add(objeto)
        self.db.commit()
        return objeto


@pytest.fixture
def criar(db) -> CriadorDeDados:
    """Atalho para montar o cenário do teste: criar.livro(...), criar.leitor(...), criar.emprestimo(...)."""
    return CriadorDeDados(db)
