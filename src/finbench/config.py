import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./finbench.db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "finbench"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
    DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    DATA_SAMPLES_DIR: Path = BASE_DIR / "data" / "samples"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    SQL_DIR: Path = BASE_DIR / "sql"

    # AI Evaluation
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = "mock-key"
    EVAL_MODEL: str = "gpt-4o-mini"
    EVAL_TIMEOUT_SECONDS: int = 30
    EVAL_MAX_RETRIES: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure directories exist
for directory in [
    settings.DATA_RAW_DIR,
    settings.DATA_PROCESSED_DIR,
    settings.DATA_SAMPLES_DIR,
    settings.REPORTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
