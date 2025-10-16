from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Environment(SQLModel, table=True):
    """Model representing an environment configuration"""

    __tablename__ = "environments"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the environment")
    name: str = Field(
        index=True,
        unique=True,
        nullable=False,
        description="Unique name of the environment (slug)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Brief description of the environment's purpose"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the environment was created (ISO DateTime)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the environment was last updated"
    )