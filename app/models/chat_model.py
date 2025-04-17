from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseClass


class Chat(BaseClass):
    __tablename__ = "chats"

    title = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_pinned = Column(Boolean, nullable=False, default=False)

    owner_uuid = Column(ForeignKey("users.uuid"), nullable=False)
    owner = relationship("User", back_populates="chats")

    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
