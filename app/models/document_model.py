from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base_model import BaseClass

class Document(BaseClass):
    __tablename__ = "documents"

    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    message_uuid = Column(PG_UUID(as_uuid=True), ForeignKey("messages.uuid"), nullable=True)
    message = relationship("Message", back_populates="documents")
    uploaded_by = Column(String, nullable=True)
