from app.models.document_model import Document
from app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session):
        super().__init__(session=session, model=Document)

