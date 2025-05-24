from fastapi import APIRouter, Depends

from app.services import ArticleService, get_article_service


router = APIRouter()


@router.post("/load")
async def load_embs(article_service: ArticleService = Depends(get_article_service)):
    return await article_service.parse_and_load_embs()

@router.get("/find")
async def find_nearest(article_service: ArticleService = Depends(get_article_service)):
    return await article_service.test_embs()