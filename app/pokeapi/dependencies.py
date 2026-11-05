import httpx

BASE_URL = "https://pokeapi.co/api/v2"


async def get_http_client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        yield client
