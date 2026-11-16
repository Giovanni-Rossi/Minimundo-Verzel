from sqlalchemy.orm import Session

from app.models import EmprestimoModel
from app.schemas import EmprestimoNovo


class EmprestimoService:
    """BIBL-2: empréstimo e devolução."""

    LIMITE_EMPRESTIMOS_ATIVOS = 3

    def __init__(self, db: Session):
        self.db = db

    def emprestar_livro(self, dados: EmprestimoNovo) -> EmprestimoModel:
        """POST /emprestimos. Operação atômica: cria o empréstimo (situacao "ativo")
        e diminui copias_disponiveis do livro em 1.

        404 (NaoEncontrado): "Livro não encontrado." | "Leitor não encontrado."
        409 (Conflito):      "Livro sem cópias disponíveis." | "Leitor já tem 3 empréstimos ativos."
        """
        raise NotImplementedError("BIBL-2 emprestar livro")

    def devolver_livro(self, emprestimo_id: int) -> EmprestimoModel:
        """POST /emprestimos/{id}/devolucao. Encerra o empréstimo (situacao "devolvido")
        e aumenta copias_disponiveis em 1. Devolver de novo não soma.

        404 (NaoEncontrado): "Empréstimo não encontrado."
        409 (Conflito):      "Empréstimo já devolvido."
        """
        raise NotImplementedError("BIBL-2 devolver livro")
