from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for all SQLAlchemy models."""
    
    # Make ID column optional in the model definition
    id: Any
    
    # Generate tablename automatically based on class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common fields for all models
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 