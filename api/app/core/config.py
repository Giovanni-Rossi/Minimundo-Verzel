from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração lida das variáveis de ambiente ou do arquivo .env (veja .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./biblioteca.db"
    # true: a API cria as tabelas que faltarem e semeia leitores (banco local).
    # false: usa as tabelas que o time de banco criou, sem mexer no schema (Postgres do time).
    criar_tabelas: bool = True
    cors_origins: str = "http://localhost:5173"

    @property
    def url_banco(self) -> str:
        """URL para o SQLAlchemy. Links "postgresql://" (como o do Neon) passam a usar o driver psycopg."""
        for prefixo in ("postgresql://", "postgres://"):
            if self.database_url.startswith(prefixo):
                return "postgresql+psycopg://" + self.database_url.removeprefix(prefixo)
        return self.database_url

    @property
    def lista_cors_origins(self) -> list[str]:
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]


settings = Settings()
