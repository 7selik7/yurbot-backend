from app.models.article_model import Article
from app.repositories.base_repository import BaseRepository
from sqlalchemy.future import select

class ArticleRepository(BaseRepository[Article]):
    def __init__(self, session):
        super().__init__(session=session, model=Article)

    async def find_nearest(self, query_embedding, top_k: int = 5):
        stmt = (
            select(self.model, self.model.embedding.l2_distance(query_embedding).label("distance"))
            .order_by("distance")
            .limit(top_k)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [(row[0], row[1]) for row in rows]