from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registra as tabelas no Base.metadata)
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.erros import registrar_handlers
from app.routers import emprestimos, leitores, livros
from app.seed import semear_leitores


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.criar_tabelas:
        # Banco local: cria as tabelas que faltarem e semeia os leitores.
        # No Postgres do time de banco (CRIAR_TABELAS=false) a API não mexe no schema.
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            semear_leitores(db)
    yield


app = FastAPI(
    title="API Biblioteca Comunitária (Minimundo Verzel)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.lista_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
registrar_handlers(app)

app.include_router(livros.router)
app.include_router(leitores.router)
app.include_router(emprestimos.router)
