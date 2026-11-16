from sqlalchemy.orm import Session

from app.models import EmprestimoModel
from app.schemas import FiltroRelatorio, ItemRanking


class RelatorioService:
    """BIBL-3 ranking, BIBL-4 relatório com filtros e BIBL-5 exportação em CSV."""

    def __init__(self, db: Session):
        self.db = db

    def ranking_livros(self) -> list[ItemRanking]:
        """GET /livros/ranking (BIBL-3). Do maior total para o menor. Nenhum empréstimo = []."""
        raise NotImplementedError("BIBL-3 ranking de livros")

    def relatorio_emprestimos(self, filtro: FiltroRelatorio) -> list[EmprestimoModel]:
        """GET /emprestimos (BIBL-4). Aplica todos os filtros ao mesmo tempo. Nenhum resultado = [].

        400 (RequisicaoInvalida): filtro inválido, ex.: inicio depois de fim.
        """
        raise NotImplementedError("BIBL-4 relatório de empréstimos")

    def exportar_emprestimos_csv(self, filtro: FiltroRelatorio) -> str:
        """GET /emprestimos/export.csv (BIBL-5). Mesmo resultado do relatorio_emprestimos.

        Cabeçalho: livro,leitor,data,situacao. UTF-8 com BOM. Sem resultados = só o cabeçalho.
        """
        raise NotImplementedError("BIBL-5 exportar CSV")
