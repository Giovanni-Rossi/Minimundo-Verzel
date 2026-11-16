from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from app.core.erros import respostas_erro
from app.dependencias import EmprestimoServiceDep, RelatorioServiceDep
from app.models import Situacao
from app.schemas import Emprestimo, EmprestimoNovo, FiltroRelatorio

router = APIRouter(prefix="/emprestimos", tags=["Empréstimos"])


def filtro_relatorio(
    leitor_id: Annotated[int | None, Query(alias="leitorId", ge=1)] = None,
    inicio: Annotated[date | None, Query(description="Data inicial (inclusiva), AAAA-MM-DD")] = None,
    fim: Annotated[date | None, Query(description="Data final (inclusiva), AAAA-MM-DD")] = None,
    situacao: Situacao | None = None,
) -> FiltroRelatorio:
    """Lê os filtros da URL. Usado pelo relatório (BIBL-4) e pelo CSV (BIBL-5)."""
    return FiltroRelatorio(leitor_id=leitor_id, inicio=inicio, fim=fim, situacao=situacao)


Filtro = Annotated[FiltroRelatorio, Depends(filtro_relatorio)]


@router.get(
    "",
    response_model=list[Emprestimo],
    operation_id="relatorioEmprestimos",
    summary="Relatório de empréstimos com filtros combináveis (BIBL-4)",
    responses=respostas_erro(400),
)
def relatorio_emprestimos(filtro: Filtro, servico: RelatorioServiceDep):
    return servico.relatorio_emprestimos(filtro)


@router.post(
    "",
    status_code=201,
    response_model=Emprestimo,
    operation_id="emprestarLivro",
    summary="Emprestar livro (BIBL-2)",
    responses=respostas_erro(404, 409),
)
def emprestar_livro(dados: EmprestimoNovo, servico: EmprestimoServiceDep):
    return servico.emprestar_livro(dados)


@router.post(
    "/{id}/devolucao",
    response_model=Emprestimo,
    operation_id="devolverLivro",
    summary="Devolver livro (BIBL-2)",
    responses=respostas_erro(404, 409),
)
def devolver_livro(id: Annotated[int, Path(ge=1)], servico: EmprestimoServiceDep):
    return servico.devolver_livro(id)


@router.get(
    "/export.csv",
    response_class=Response,
    operation_id="exportarEmprestimosCsv",
    summary="Exportar relatório em CSV (BIBL-5)",
    responses={
        200: {"description": "Arquivo CSV", "content": {"text/csv": {"schema": {"type": "string"}}}},
        **respostas_erro(400),
    },
)
def exportar_emprestimos_csv(filtro: Filtro, servico: RelatorioServiceDep) -> Response:
    conteudo = servico.exportar_emprestimos_csv(filtro)
    return Response(
        content=conteudo,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="emprestimos.csv"'},
    )
