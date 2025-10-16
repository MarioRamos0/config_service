from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """Model representing a user in the system"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the user")
    
    username: str = Field(
        max_length=100,
        unique=True,
        nullable=False,
        description="Unique username for login"
    )
    
    password_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Secure hash of the user's password"
    )
    
    is_admin: bool = Field(
        default=False,
        description="Indicates if the user has admin privileges"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the user was created"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the user was last updated"
    )