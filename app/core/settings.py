from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import SQLModel, create_engine
import os
from typing import ClassVar

from app.variables.models.variable import Variable
from app.environments.models.environment import Environment
from app.users.models.user import User

# --- FUNCIONES DE CARGA DE SECRETO ---
def decode_secret_file(value: str, fallback_value: str) -> str:
    """
    Decodifica el contenido de una variable que puede ser:
    1. El contenido directo de un secreto (e.g., una URL de BD o un secreto JWT).
    2. Una ruta a un archivo de secreto (e.g., /run/secrets/database_url).
    """
    # 1. Si es una ruta de archivo (Docker Swarm o Compose)
    if value.startswith("/") and os.path.exists(value):
        try:
            with open(value, 'r') as f:
                return f.read().strip()
        except Exception as e:
            # En caso de error de permisos o lectura, imprime y usa fallback
            print(f"ERROR: Fallo al leer el archivo de secreto en {value}: {e}")
            return fallback_value
    
    # 2. Si es el valor directo (e.g., dev/test) o no existe el archivo en la ruta
    if value:
        return value
        
    # 3. Fallback final
    return fallback_value


class Settings(BaseSettings):
    # Pydantic carga directamente estos campos. Sus valores iniciales serán
    # las RUTAS de los secretos (e.g., /run/secrets/...) o el valor directo.
    DATABASE_URL: str
    JWT_SECRET: str
    
    DEBUG: bool = False
    ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
# 1. Cargar la configuración. DATABASE_URL y JWT_SECRET contienen la RUTA al archivo de secreto.
settings = Settings()

# 2. Decodificar el contenido real de los secretos (rompiendo el ciclo de Pydantic)
# y SOBREESCRIBIR el valor de la propiedad en el objeto settings.
# Esto asegura que el resto de la aplicación (como jwt.py) lea el CONTENIDO final.
settings.DATABASE_URL = decode_secret_file(
    settings.DATABASE_URL, 
    "sqlite:///./local.db" # Fallback para DB si todo falla
)

settings.JWT_SECRET = decode_secret_file(
    settings.JWT_SECRET, 
    "DEFAULT_JWT_SECRET_FOR_DEV" # Fallback para JWT si todo falla
)


# 3. Inicializar el motor de la BD usando el contenido DECODIFICADO
# Ahora settings.DATABASE_URL contiene el valor final real.
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)