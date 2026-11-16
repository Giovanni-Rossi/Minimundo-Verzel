import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import LeitorModel, LivroModel, PerfilUsuario

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
