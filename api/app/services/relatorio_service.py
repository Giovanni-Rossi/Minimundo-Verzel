import csv
import io
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models import EmprestimoModel
from app.schemas import FiltroRelatorio, ItemRanking

CABECALHO_CSV = ["livro", "leitor", "data", "situacao"]
BOM_UTF8 = "﻿"  # faz o Excel abrir os acentos corretamente


def montar_csv(emprestimos: Iterable[EmprestimoModel]) -> str:
    """Uma linha por empréstimo: título do livro, nome do leitor, data (AAAA-MM-DD) e situação.

    Usa o módulo csv para escapar vírgulas e aspas (ex.: um título "Ah, é?").
    """
    saida = io.StringIO()
    escritor = csv.writer(saida)  # separador "," e quebra de linha "\r\n" (padrão do CSV)
    escritor.writerow(CABECALHO_CSV)
    for emprestimo in emprestimos:
        escritor.writerow([
            emprestimo.livro.titulo,
            emprestimo.leitor.nome,
            emprestimo.data_emprestimo.date().isoformat(),
            emprestimo.situacao.value,
        ])
    return BOM_UTF8 + saida.getvalue()


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

        Reaproveita o relatório (BIBL-4) para garantir os mesmos filtros e a mesma validação:
        filtro inválido já sai como 400 de lá.
        """
        return montar_csv(self.relatorio_emprestimos(filtro))
