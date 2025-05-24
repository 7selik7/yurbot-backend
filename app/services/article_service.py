import json

from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.article_repository import ArticleRepository

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class ArticleService:
    def __init__(self, session: AsyncSession, article_repository: ArticleRepository):
        self.session = session
        self.article_repository = article_repository

    async def parse_and_load_embs(self):
        with open('train_data/criminal_codex.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
            for item in articles:
                combined_text = f"{item['chapter_name']}.\n{item['article']}.\n{item['content']}"
                embedding = model.encode(combined_text, normalize_embeddings=True).tolist()
                await self.article_repository.create_one({
                    "article": item['article'],
                    "content": item['content'],
                    "chapter": item.get('chapter'),
                    "chapter_name": item.get('chapter_name'),
                    "embedding": embedding
                })


    async def find_nearest_articles(self, text: str, similarity_threshold: float = 0.9) -> str:
        query_embedding = model.encode(text, normalize_embeddings=True).tolist()
        results = await self.article_repository.find_nearest(query_embedding=query_embedding, top_k=10)

        if not results:
            return "Не знайдено релевантних статей у Кримінальному Кодексі України."

        filtered_results = [
            (article, distance) for article, distance in results if distance <= similarity_threshold
        ]

        if not filtered_results:
            return "Не знайдено релевантних статей, які достатньо співпадають із запитом."

        context_info = "\n\n".join(
            f"Глава: {article.chapter_name or 'Невідомо'}\n"
            f"Стаття: {article.article or 'Невідомо'}\n"
            f"{article.content[:500]}...\n"
            f"(Схожість: {distance:.4f})"
            for article, distance in filtered_results
        )

        return context_info

    async def test_embs(self):
        test_sentence = (
            "Вирок суду іноземної держави може бути врахований, якщо?"
        )
        query_embedding = model.encode(test_sentence, normalize_embeddings=True).tolist()

        results = await self.article_repository.find_nearest(query_embedding=query_embedding, top_k=10)

        for idx, (article, distance) in enumerate(results, 1):
            print(f"--- Результат {idx} ---")
            print(f"Дистанция (схожесть): {distance:.4f}")
            print(f"Глава: {article.chapter_name}")
            print(f"Статья: {article.article}")
            print(f"Текст: {article.content[:300]}...\n")
