from datetime import datetime
from itertools import count

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import EmprestimoModel, LeitorModel, LivroModel, PerfilUsuario, Situacao

engine_teste = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SessaoTeste = sessionmaker(bind=engine_teste, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db():
    """Banco em memória, criado vazio a cada teste a partir dos models."""
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


@pytest.fixture
def novo_leitor(db):
    """Cria um usuário. Ex.: novo_leitor("Ana") ou novo_leitor("Bia", PerfilUsuario.BIBLIOTECARIO)."""

    def criar(nome: str = "Ana", perfil: PerfilUsuario = PerfilUsuario.LEITOR) -> LeitorModel:
        leitor = LeitorModel(
            nome=nome, email=f"{nome.lower()}@teste.com", senha_hash="!", perfil=perfil
        )
        db.add(leitor)
        db.commit()
        return leitor

    return criar


@pytest.fixture
def novo_livro(db):
    """Cria um livro. Ex.: novo_livro(copias=0)."""

    def criar(
        titulo: str = "Dom Casmurro",
        copias: int = 1,
        autor: str = "Machado de Assis",
        ano: int = 1899,
    ) -> LivroModel:
        livro = LivroModel(titulo=titulo, autor=autor, ano=ano, copias_disponiveis=copias)
        db.add(livro)
        db.commit()
        return livro

    return criar


class CriadorDeDados:
    """Insere dados direto no banco de teste, sem depender das rotas de outras histórias."""

    def __init__(self, db: Session):
        self.db = db
        self._emails = count(1)

    def livro(self, titulo: str, copias: int = 3) -> LivroModel:
        livro = LivroModel(titulo=titulo, autor="Autor", ano=2000, copias_disponiveis=copias)
        return self._salvar(livro)

    def leitor(self, nome: str) -> LeitorModel:
        # email e senha_hash são obrigatórios no banco real; aqui só precisam ser válidos.
        email = f"leitor{next(self._emails)}@teste.com"
        return self._salvar(LeitorModel(nome=nome, email=email, senha_hash="!"))

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
