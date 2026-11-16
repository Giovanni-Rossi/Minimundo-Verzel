"""Erros da API. Toda resposta de erro sai no formato do contrato: {"erro": "mensagem"}.

Nos services, lance a exceção do status certo com a mensagem exata do contrato:
    raise NaoEncontrado("Livro não encontrado.")
    raise Conflito("Leitor já tem 3 empréstimos ativos.")
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.erro import Erro


class ErroApi(Exception):
    status_code = 400

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class RequisicaoInvalida(ErroApi):
    status_code = 400


class NaoEncontrado(ErroApi):
    status_code = 404


class Conflito(ErroApi):
    status_code = 409


def respostas_erro(*codigos: int) -> dict:
    """Documenta no /docs os erros que a rota pode devolver. Ex.: respostas_erro(404, 409)."""
    return {codigo: {"model": Erro} for codigo in codigos}


def _json_erro(status_code: int, mensagem: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"erro": mensagem})


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroApi)
    async def erro_api(_: Request, exc: ErroApi) -> JSONResponse:
        return _json_erro(exc.status_code, exc.mensagem)

    @app.exception_handler(RequestValidationError)
    async def erro_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
        # O contrato usa 400 para dados inválidos (o padrão do FastAPI seria 422).
        erros = exc.errors()
        campo = erros[0]["loc"][-1] if erros else "requisição"
        return _json_erro(400, f"Campo inválido: {campo}.")

    @app.exception_handler(NotImplementedError)
    async def nao_implementado(_: Request, exc: NotImplementedError) -> JSONResponse:
        return _json_erro(501, f"Ainda não implementado: {exc}.")
