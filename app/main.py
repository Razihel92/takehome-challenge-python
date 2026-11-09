from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import settings
from app.exceptions import AppError
from app.seed.router import router as seed_router
from app.users.router import router as users_router

app = FastAPI()
app.include_router(users_router)

if settings.app_env != "production":
    app.include_router(seed_router)


posts: list[dict[str, int | str]] = [
    {"id": 1, "name": "Andres"},
    {"id": 2, "name": "Felipe"},
]


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/post", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{posts[0]['name']}</h1>"


@app.get("/api/posts")
def get_posts():
    return posts


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
