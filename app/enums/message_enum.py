import enum


class AuthorType(str, enum.Enum):
    USER = "user"
    SYSTEM = "system"
    AI = "ai"


class MarkType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    NONE = "none"
