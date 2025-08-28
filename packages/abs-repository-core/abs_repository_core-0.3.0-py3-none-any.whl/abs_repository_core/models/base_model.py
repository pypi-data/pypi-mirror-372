import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String,Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Base model for all models
    """
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

class BaseDraftModel(BaseModel):
    """
    Base model for all models that need to have a draft status
    """
    __abstract__ = True
    is_draft = Column(Boolean, default=False, server_default="false", nullable=False)
