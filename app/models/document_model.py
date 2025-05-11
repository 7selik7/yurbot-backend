from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base_model import BaseClass


class Document(BaseClass):
    __tablename__ = "documents"

    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    size = Column(String, nullable=True)
    message_uuid = Column(ForeignKey("messages.uuid"), nullable=False)
    message = relationship("Message", back_populates="documents")

