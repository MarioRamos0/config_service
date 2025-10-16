from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Environment(SQLModel, table=True):

    __tablename__ = "environments"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        index=True,
        unique=True,
        nullable=False,
        description="Nombre único del entorno (slug)."
    )
    description: Optional[str] = Field(
        default=None,
        description="Breve descripción del propósito del entorno."
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Fecha de creación del entorno (ISO DateTime)."
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Fecha de última actualización del entorno."
    )
