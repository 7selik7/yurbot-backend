import uuid

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

Base: DeclarativeMeta = declarative_base()


class BaseClass(Base):
    __abstract__ = True

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
