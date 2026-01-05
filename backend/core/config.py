import os
from functools import lru_cache


class Settings:
    # ---- Database core ----
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5433))
    DB_NAME: str = os.getenv("DB_NAME", "jobsdb")

    # ---- Admin role (migrations / DDL) ----
    ADMIN_DB_USER: str = os.getenv("ADMIN_DB_USER", "app_admin")
    ADMIN_DB_PASSWORD: str = os.getenv("ADMIN_DB_PASSWORD", "very_strong_password")

    # ---- SQLAlchemy ----
    DB_DRIVER: str = "postgresql+psycopg2"
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "true").lower() == "true"

    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "app") 
    
    @property
    def ADMIN_DATABASE_URL(self) -> str:
        return (
            f"{self.DB_DRIVER}://{self.ADMIN_DB_USER}:"
            f"{self.ADMIN_DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
            f"?options=-csearch_path={self.DB_SCHEMA}"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
