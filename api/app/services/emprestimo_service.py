from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.erros import Conflito, NaoEncontrado
from app.models import EmprestimoModel, LeitorModel, LivroModel, PerfilUsuario, Situacao
from app.schemas import EmprestimoNovo


class EmprestimoService:
    """BIBL-2: empréstimo e devolução.

    Cada operação é uma transação só. As linhas do livro, do leitor e do empréstimo ficam
    travadas (SELECT ... FOR UPDATE) até o commit, para dois pedidos ao mesmo tempo não
    levarem a última cópia nem passarem do limite. No SQLite o travamento é ignorado.
    """

    LIMITE_EMPRESTIMOS_ATIVOS = 3

    def __init__(self, db: Session):
        self.db = db

    def emprestar_livro(self, dados: EmprestimoNovo) -> EmprestimoModel:
        """POST /emprestimos. Cria o empréstimo (situacao "ativo") e tira 1 das cópias do livro.

        404 (NaoEncontrado): "Livro não encontrado." | "Leitor não encontrado."
        409 (Conflito):      "Livro sem cópias disponíveis." | "Leitor já tem 3 empréstimos ativos."
        """
        livro = self.db.get(LivroModel, dados.livro_id, with_for_update=True)
        if livro is None:
            raise NaoEncontrado("Livro não encontrado.")

        leitor = self.db.get(LeitorModel, dados.leitor_id, with_for_update=True)
        if leitor is None or leitor.perfil != PerfilUsuario.LEITOR:
            raise NaoEncontrado("Leitor não encontrado.")

        if livro.copias_disponiveis <= 0:
            raise Conflito("Livro sem cópias disponíveis.")

        if self._contar_ativos(leitor.id) >= self.LIMITE_EMPRESTIMOS_ATIVOS:
            raise Conflito(f"Leitor já tem {self.LIMITE_EMPRESTIMOS_ATIVOS} empréstimos ativos.")

        emprestimo = EmprestimoModel(
            livro=livro,
            leitor=leitor,
            situacao=Situacao.ATIVO,
            data_emprestimo=datetime.now(UTC),
            data_devolucao=None,
        )
        livro.copias_disponiveis -= 1
        self.db.add(emprestimo)
        self.db.commit()
        return emprestimo

    def devolver_livro(self, emprestimo_id: int) -> EmprestimoModel:
        """POST /emprestimos/{id}/devolucao. Encerra o empréstimo (situacao "devolvido")
        e soma 1 nas cópias do livro. Devolver de novo não soma.

        404 (NaoEncontrado): "Empréstimo não encontrado."
        409 (Conflito):      "Empréstimo já devolvido."
        """
        emprestimo = self.db.get(EmprestimoModel, emprestimo_id, with_for_update=True)
        if emprestimo is None:
            raise NaoEncontrado("Empréstimo não encontrado.")
        if emprestimo.situacao == Situacao.DEVOLVIDO:
            raise Conflito("Empréstimo já devolvido.")

        livro = self.db.get(LivroModel, emprestimo.livro_id, with_for_update=True)
        # O banco exige que situacao e data_devolucao mudem juntas (CHECK status_coerente).
        emprestimo.situacao = Situacao.DEVOLVIDO
        emprestimo.data_devolucao = datetime.now(UTC)
        livro.copias_disponiveis += 1
        self.db.commit()
        return emprestimo

    def _contar_ativos(self, leitor_id: int) -> int:
        consulta = (
            select(func.count())
            .select_from(EmprestimoModel)
            .where(
                EmprestimoModel.leitor_id == leitor_id,
                EmprestimoModel.situacao == Situacao.ATIVO,
            )
        )
        return self.db.scalar(consulta) or 0
