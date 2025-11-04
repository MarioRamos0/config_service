from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import SQLModel, create_engine
import os
from typing import ClassVar, Optional # Importar Optional

from app.variables.models.variable import Variable
from app.environments.models.environment import Environment
from app.users.models.user import User


class Settings(BaseSettings):
    # Campos internos (con guion bajo) que Pydantic valida.
    # Son opcionales para evitar el error "Field required".
    _DATABASE_URL: Optional[str] = None  
    _JWT_SECRET: Optional[str] = None      
    
    # Campos que Pydantic lee del entorno (.env) o Docker Swarm (Rutas de Archivos).
    DATABASE_URL_FILE: str
    DEBUG: bool = False
    ENV: str = "development"
    JWT_SECRET_FILE: str
    
    # Nombres de secretos para buscar en /run/secrets
    DB_URL_SECRET_NAME: ClassVar[str] = "database_url"
    JWT_SECRET_NAME: ClassVar[str] = "jwt_secret" 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        # Lógica para leer el secreto de Docker Swarm (prioridad alta)
        secret_path = os.path.join("/run/secrets", self.DB_URL_SECRET_NAME)
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()

            # Fallback para entorno de desarrollo (lee DATABASE_URL del entorno)
            if os.getenv("DATABASE_URL"):
                return os.getenv("DATABASE_URL")
        except Exception as e:
            print(f"Error al leer el secreto de la base de datos: {e}")
            return "sqlite:///./error_db.db"

        # Fallback por defecto
        return "sqlite:///./local.db"

    @property
    def JWT_SECRET(self) -> str:
        # Lógica para leer el secreto de Docker Swarm (prioridad alta)
        secret_path = os.path.join("/run/secrets", self.JWT_SECRET_NAME)
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()

            # Fallback para entorno de desarrollo (lee JWT_SECRET del entorno)
            if os.getenv("JWT_SECRET"):
                return os.getenv("JWT_SECRET")

        except Exception as e:
            print(f"Error al leer el secreto JWT: {e}")
            return "FALLBACK_JWT_SECRET_ERROR"

        # Fallback por defecto
        return "DEFAULT_JWT_SECRET_FOR_DEV"


settings = Settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)
