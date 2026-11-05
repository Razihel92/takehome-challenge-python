from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.exceptions import AppError
from app.users.router import router as users_router

app = FastAPI()
app.include_router(users_router)

posts: list[dict] = [{"id": 1, "name": "Andres"}, {"id": 2, "name": "Felipe"}]


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
