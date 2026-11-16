from app.schemas.base import SchemaBase


class ItemRanking(SchemaBase):
    """Um livro no ranking dos mais emprestados (BIBL-3)."""

    livro_id: int
    titulo: str
    total_emprestimos: int
