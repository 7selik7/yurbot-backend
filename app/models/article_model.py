from sqlalchemy import Column, String, Text
from pgvector.sqlalchemy import Vector

from app.models.base_model import BaseClass

class Article(BaseClass):
    __tablename__ = "articles"

    article = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    chapter = Column(String, nullable=True)
    chapter_name = Column(String, nullable=True)
    embedding = Column(Vector(384), nullable=False)
