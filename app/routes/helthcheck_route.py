from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root_handler():
    return {"status_code": 200, "detail": "ok", "result": "working"}