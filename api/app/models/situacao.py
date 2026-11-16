from enum import StrEnum


class Situacao(StrEnum):
    """Situação de um empréstimo.

    Na API (contrato) sai o valor: "ativo" / "devolvido".
    No banco é gravado o nome: ATIVO / DEVOLVIDO (tipo status_emprestimo).
    """

    ATIVO = "ativo"
    DEVOLVIDO = "devolvido"
