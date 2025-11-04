from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import SQLModel, create_engine
import os
from typing import ClassVar

from app.variables.models.variable import Variable
from app.environments.models.environment import Environment
from app.users.models.user import User


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    JWT_SECRET: Optional[str] = None
    DATABASE_URL_FILE: str
    DEBUG: bool = False
    ENV: str = "development"
    JWT_SECRET_FILE: str
    DB_URL_SECRET_NAME: ClassVar[str] = "database_url"
    JWT_SECRET_NAME: ClassVar[str] = "jwt_secret" 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        secret_path = os.path.join("/run/secrets", self.DB_URL_SECRET_NAME)
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()

            if os.getenv("DATABASE_URL"):
                return os.getenv("DATABASE_URL")
        except Exception as e:
            print(f"Error al leer el secreto de la base de datos: {e}")
            return "sqlite:///./error_db.db"

        return "sqlite:///./local.db"

    @property
    def JWT_SECRET(self) -> str:
        secret_path = os.path.join("/run/secrets", self.JWT_SECRET_NAME)
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()

            if self.JWT_SECRET_FILE:
                return self.JWT_SECRET_FILE
            
        except Exception as e:
            print(f"Error al leer el secreto JWT: {e}")
            return "FALLBACK_JWT_SECRET_ERROR"

        return "DEFAULT_JWT_SECRET_FOR_DEV"


settings = Settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)
