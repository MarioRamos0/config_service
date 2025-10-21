
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer

if TYPE_CHECKING:
    from app.environments.models.environment import Environment

class Variable(SQLModel, table=True):
    __tablename__ = "variable"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(
        index=True,
        unique=True,
        nullable=False,
        description="Nombre único de la variable en un entorno (slug URL)."
    )

    value: str = Field(
        nullable=False,
        description="Valor de la variable."
    )

    description: Optional[str] = Field(
        default=None,
        description="Breve explicación de para qué sirve la variable."
    )

    is_sensitive: bool = Field(
        default=False,
        description="Indica si la variable es sensible (e.g., contraseñas)."
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Fecha de creación de la variable (ISO DateTime)."
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Fecha de última actualización de la variable."
    )
    environment_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("environments.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )

    environment: Optional["Environment"] = Relationship(
        back_populates="variables",
        sa_relationship_kwargs={"passive_deletes": True},
    )

