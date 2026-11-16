from enum import StrEnum


class Situacao(StrEnum):
    """Situação de um empréstimo. Contrato: components.schemas.Situacao."""

    ATIVO = "ativo"
    DEVOLVIDO = "devolvido"
