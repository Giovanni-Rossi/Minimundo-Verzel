from enum import StrEnum


class PerfilUsuario(StrEnum):
    """Perfil de um usuário. No banco: tipo perfil_usuario (valores leitor/bibliotecario)."""

    LEITOR = "leitor"
    BIBLIOTECARIO = "bibliotecario"
