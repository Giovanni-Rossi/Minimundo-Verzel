from fastapi import APIRouter

from app.core.erros import respostas_erro
from app.dependencias import LivroServiceDep, RelatorioServiceDep
from app.schemas import ItemRanking, Livro, LivroNovo

router = APIRouter(prefix="/livros", tags=["Livros"])


@router.get(
    "",
    response_model=list[Livro],
    operation_id="listarLivros",
    summary="Listar o acervo (BIBL-1)",
)
def listar_livros(servico: LivroServiceDep):
    return servico.listar_livros()


@router.post(
    "",
    status_code=201,
    response_model=Livro,
    operation_id="cadastrarLivro",
    summary="Cadastrar livro (BIBL-1)",
    responses=respostas_erro(400),
)
def cadastrar_livro(dados: LivroNovo, servico: LivroServiceDep):
    return servico.cadastrar_livro(dados)


# Mantenha esta rota antes de qualquer /livros/{id}, senão "ranking" é lido como id.
@router.get(
    "/ranking",
    response_model=list[ItemRanking],
    operation_id="rankingLivros",
    summary="Ranking dos mais emprestados (BIBL-3)",
)
def ranking_livros(servico: RelatorioServiceDep):
    return servico.ranking_livros()
