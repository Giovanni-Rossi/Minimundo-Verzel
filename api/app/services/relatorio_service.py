import csv
import io
from collections.abc import Iterable
from datetime import datetime, time, timedelta

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.core.erros import RequisicaoInvalida
from app.models import EmprestimoModel, LivroModel, Situacao
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
        """GET /livros/ranking (BIBL-3). Do maior total para o menor. Nenhum empréstimo = [].

        Conta empréstimos ativos e devolvidos (o ranking mede a procura). Livro nunca emprestado
        não aparece. Empate é desempatado pelo título, para a ordem não mudar entre chamadas.
        """
        total = func.count(EmprestimoModel.id).label("total_emprestimos")
        consulta = (
            select(LivroModel.id, LivroModel.titulo, total)
            .join(EmprestimoModel, EmprestimoModel.livro_id == LivroModel.id)
            .group_by(LivroModel.id, LivroModel.titulo)
            .order_by(total.desc(), LivroModel.titulo)
        )
        return [
            ItemRanking(livro_id=livro_id, titulo=titulo, total_emprestimos=total_emprestimos)
            for livro_id, titulo, total_emprestimos in self.db.execute(consulta)
        ]

    def relatorio_emprestimos(self, filtro: FiltroRelatorio) -> list[EmprestimoModel]:
        """GET /emprestimos (BIBL-4). Aplica todos os filtros ao mesmo tempo. Nenhum resultado = [].

        400 (RequisicaoInvalida): filtro inválido, ex.: inicio depois de fim.
        """
        if filtro.inicio and filtro.fim and filtro.inicio > filtro.fim:
            raise RequisicaoInvalida("Data inicial não pode ser depois da data final.")
        return list(self.db.scalars(self._consultar_emprestimos(filtro)).unique())

    def exportar_emprestimos_csv(self, filtro: FiltroRelatorio) -> str:
        """GET /emprestimos/export.csv (BIBL-5). Mesmo resultado do relatorio_emprestimos.

        Cabeçalho: livro,leitor,data,situacao. UTF-8 com BOM. Sem resultados = só o cabeçalho.

        Reaproveita o relatório (BIBL-4) para garantir os mesmos filtros e a mesma validação:
        filtro inválido já sai como 400 de lá.
        """
        return montar_csv(self.relatorio_emprestimos(filtro))

    def _consultar_emprestimos(self, filtro: FiltroRelatorio) -> Select[tuple[EmprestimoModel]]:
        """Consulta do relatório, do mais recente para o mais antigo.

        A situação vem de data_devolucao (vazia = ativo); o banco garante que ela bate com status.
        """
        consulta = select(EmprestimoModel).options(
            joinedload(EmprestimoModel.livro), joinedload(EmprestimoModel.leitor)
        )
        if filtro.leitor_id is not None:
            consulta = consulta.where(EmprestimoModel.leitor_id == filtro.leitor_id)
        if filtro.inicio is not None:
            consulta = consulta.where(
                EmprestimoModel.data_emprestimo >= datetime.combine(filtro.inicio, time.min)
            )
        if filtro.fim is not None:
            # "fim" é inclusivo: vale até o último instante do dia, ou seja, antes do dia seguinte.
            dia_seguinte = datetime.combine(filtro.fim + timedelta(days=1), time.min)
            consulta = consulta.where(EmprestimoModel.data_emprestimo < dia_seguinte)
        if filtro.situacao == Situacao.ATIVO:
            consulta = consulta.where(EmprestimoModel.data_devolucao.is_(None))
        elif filtro.situacao == Situacao.DEVOLVIDO:
            consulta = consulta.where(EmprestimoModel.data_devolucao.is_not(None))
        return consulta.order_by(EmprestimoModel.data_emprestimo.desc(), EmprestimoModel.id.desc())
