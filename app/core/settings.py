from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import SQLModel, create_engine
from app.variables.models.variable import Variable
from app.environments.models.environment import Environment
from app.users.models.user import User


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    ENV: str = "development"
    JWT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def init_db():
    SQLModel.metadata.create_all(engine)