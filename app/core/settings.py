from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import SQLModel, create_engine
import os
from typing import ClassVar
from functools import cached_property # IMPORTE CLAVE

from app.variables.models.variable import Variable
from app.environments.models.environment import Environment
from app.users.models.user import User


class Settings(BaseSettings):
    # Campos que Pydantic carga directamente del entorno (.env) o Docker.
    # Eliminamos cualquier campo llamado DATABASE_URL o JWT_SECRET para
    # evitar la colisión con las propiedades calculadas.
    DEBUG: bool = False
    ENV: str = "development"
    
    # Nombres de secretos para buscar en /run/secrets (ClassVar no se valida)
    DB_URL_SECRET_NAME: ClassVar[str] = "database_url"
    JWT_SECRET_NAME: ClassVar[str] = "jwt_secret" 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # USAMOS @cached_property para que Pydantic lo trate como un atributo
    # calculado de solo lectura que se evalúa DESPUÉS de la inicialización,
    # resolviendo el conflicto de validación.
    @cached_property
    def DATABASE_URL(self) -> str:
        # 1. Prioridad: Lógica para leer el secreto de Docker Swarm (de /run/secrets/database_url)
        secret_path = os.path.join("/run/secrets", self.DB_URL_SECRET_NAME)
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()
            
            # 2. Fallback: Si no hay secreto fijo, busca la variable de entorno
            env_val = os.getenv("DATABASE_URL")
            if env_val:
                # Si el valor de ENV es una RUTA (como en su compose), leemos el contenido.
                if env_val.startswith("/run/secrets"):
                     with open(env_val, 'r') as f:
                        return f.read().strip()
                # Si es una URL directa (como en desarrollo local), la devolvemos.
                return env_val
                
        except Exception as e:
            # Captura errores de lectura/permisos
            print(f"Error al leer el secreto de la base de datos: {e}")
            return "sqlite:///./error_db.db"

        # 3. Fallback final
        return "sqlite:///./local.db"

    @cached_property
    def JWT_SECRET(self) -> str:
        # 1. Prioridad: Lógica para leer el secreto de Docker Swarm (de /run/secrets/jwt_secret)
        secret_path = os.path.join("/run/secrets", self.JWT_SECRET_NAME)
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()
            
            # 2. Fallback: Si no hay secreto fijo, busca la variable de entorno
            env_val = os.getenv("JWT_SECRET")
            if env_val:
                 # Si el valor de ENV es una RUTA (como en su compose), leemos el contenido.
                if env_val.startswith("/run/secrets"):
                     with open(env_val, 'r') as f:
                        return f.read().strip()
                # Si es un secreto directo, lo devolvemos.
                return env_val

        except Exception as e:
            print(f"Error al leer el secreto JWT: {e}")
            return "FALLBACK_JWT_SECRET_ERROR"

        # 3. Fallback final
        return "DEFAULT_JWT_SECRET_FOR_DEV"


settings = Settings()

# A partir de aquí, settings.DATABASE_URL ya está disponible con la URL final.
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)