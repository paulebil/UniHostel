import os
from functools import lru_cache
from pydantic import Field, model_validator, EmailStr, SecretStr
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

# Correct path to .env (backend/.env)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path, verbose=True)


class Settings(BaseSettings):
    # App
    APP_NAME: str = Field(..., env="APP_NAME")
    DEBUG: bool = Field(False, env="DEBUG")
    FRONTEND_HOST: str = Field(..., env="FRONTEND_HOST")
    FRONTED_HOST_LOGIN: str = Field(..., env="FRONTED_HOST_LOGIN")

    # JWT Secret key
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(..., env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(..., env="REFRESH_TOKEN_EXPIRE_MINUTES")

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
    MINIO_IMAGE_BUCKET_NAME: str = Field(..., env="MINIO_IMAGE_BUCKET_NAME")
    MINIO_PDF_BUCKET_NAME: str = Field(..., env="MINIO_PDF_BUCKET_NAME")
    MINIO_PUBLIC_ENDPOINT: str = Field(..., env="MINIO_PUBLIC_ENDPOINT")

    # Security
    ALLOWED_HOSTS: str = Field(..., env="ALLOWED_HOSTS")

    # SMTP
    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = Field(..., env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field("", env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[SecretStr] = Field(SecretStr(""), env="SMTP_PASSWORD")
    SMTP_FROM: EmailStr = Field(..., env="SMTP_FROM")
    SMTP_FROM_NAME: str = Field(..., env="SMTP_FROM_NAME")
    SMTP_SERVER: str = Field(..., env="SMTP_SERVER")
    SMTP_STARTTLS: bool = Field(default=False, env="SMTP_STARTTLS")
    SMTP_SSL_TLS: bool = Field(default=False, env="SMTP_SSL_TLS")
    USE_CREDENTIALS: bool = Field(default=False, env="USE_CREDENTIALS")
    SMTP_DEBUG: bool = Field(default=False, env="SMTP_DEBUG")

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

    # Un-comment this lines of code to print the loaded settings

    # def __init__(self, **values):
    #     super().__init__(**values)
    #     print("\nLoaded settings:")
    #     for key, value in self.model_dump().items():
    #         print(f"{key}: {value} ({type(value).__name__})")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    #print("\nFinal DATABASE_URI:", settings.DATABASE_URI)