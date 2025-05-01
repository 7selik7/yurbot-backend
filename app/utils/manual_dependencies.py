from typing import AsyncGenerator, Any, TypeVar
from contextlib import asynccontextmanager

T = TypeVar("T")

@asynccontextmanager
async def resolve_async_generator(gen: AsyncGenerator[T, Any]):
    obj = await gen.__anext__()
    try:
        yield obj
    finally:
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass