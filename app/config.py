from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = ""  # vacío: la API arranca sin base (sirve /health y los tests)
    mongodb_db: str = "mipeli"
    firebase_project_id: str = ""
    cors_origins: str = "http://localhost:8000"  # separados por coma
    tmdb_token: str = ""
    omdb_key: str = ""
    tastedive_key: str = ""

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
