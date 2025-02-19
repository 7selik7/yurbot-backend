from sqlalchemy import Column, String, Boolean

from app.models.base_model import BaseClass


class User(BaseClass):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_first_login = Column(Boolean, nullable=False, default=True)
    is_confirmed = Column(Boolean, nullable=False, default=False)

