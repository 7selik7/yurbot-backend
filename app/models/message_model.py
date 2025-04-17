from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.enums.message_enum import MarkType, AuthorType
from app.models.base_model import BaseClass


class Message(BaseClass):
    __tablename__ = "messages"

    text = Column(String, nullable=False)

    mark = Column(
        Enum(MarkType, name="mark_enum"),
        nullable=False,
        default=MarkType.NONE
    )

    author = Column(
        Enum(AuthorType, name="author_enum"),
        nullable=False
    )

    parent_uuid = Column(ForeignKey("messages.uuid"), nullable=True)
    parent = relationship("Message", remote_side="Message.uuid", backref="children")

    chat_uuid = Column(ForeignKey("chats.uuid"), nullable=False)
    chat = relationship("Chat", back_populates="messages")
