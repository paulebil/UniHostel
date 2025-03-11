import os
from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pathlib import Path

# Correct path to .env (backend/.env)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path, verbose=True)

# Verify environment variables
# print(f"Loaded .env from: {env_path}")
# print("DB_USER:", os.getenv("DB_USER"))
# print("EMAIL_FROM_NAME:", os.getenv("EMAIL_FROM_NAME"))

class Settings(BaseSettings):
    # App
    APP_NAME: str = Field(..., env="APP_NAME")
    DEBUG: bool = Field(False, env="DEBUG")
    FRONTEND_HOST: str = Field(..., env="FRONTEND_HOST")

    # PostgreSQL
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")

    # MinIO
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    MINIO_ROOT_USER: str = Field(..., env="MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD: str = Field(..., env="MINIO_ROOT_PASSWORD")
    MINIO_BUCKET_NAME: str = Field(..., env="MINIO_BUCKET_NAME")

    # Security
    ALLOWED_HOSTS: str = Field(..., env="ALLOWED_HOSTS")

    # SMTP
    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: str | None = Field(None, env="SMTP_USERNAME")
    SMTP_PASSWORD: str | None = Field(None, env="SMTP_PASSWORD")
    EMAIL_FROM: str = Field(..., env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = Field(..., env="EMAIL_FROM_NAME")

    # Database URI
    DATABASE_URI: str = ""

    @model_validator(mode='after')
    def set_database_uri(self) -> 'Settings':
        if not self.DATABASE_URI:
            self.DATABASE_URI = (
                f"postgresql://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self

    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, values: dict) -> dict:
        # Handle empty SMTP credentials
        for field in ['SMTP_USERNAME', 'SMTP_PASSWORD']:
            if values.get(field) == "":
                values[field] = None

        # Convert boolean-like strings
        if (debug := values.get('DEBUG')) not in (None, ''):
            values['DEBUG'] = str(debug).lower() in {'true', '1'}

        # Convert integer-like strings
        for field in ['DB_PORT', 'SMTP_PORT']:
            if (value := values.get(field)) not in (None, ''):
                values[field] = int(value)

        return values

    def __init__(self, **values):
        super().__init__(**values)
        print("\nLoaded settings:")
        for key, value in self.model_dump().items():
            print(f"{key}: {value} ({type(value).__name__})")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    print("\nFinal DATABASE_URI:", settings.DATABASE_URI)