from app.schemas.base import SchemaBase


class Erro(SchemaBase):
    """Formato de todo erro da API: {"erro": "mensagem para mostrar na tela"}."""

    erro: str
