import httpx

from app.config import settings


async def get_http_client():
    async with httpx.AsyncClient(base_url=settings.pokeapi_url, timeout=5.0) as client:
        yield client
