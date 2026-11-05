FROM python:3.14-slim

# uv: se copia el binario desde su imagen oficial
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# 1. Dependencias primero: esta capa queda en caché mientras no cambien
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# 2. Código de la aplicación
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

EXPOSE 8000

# Aplica las migraciones pendientes y arranca la API
CMD ["sh", "-c", "alembic upgrade head && fastapi run app/main.py --host 0.0.0.0 --port 8000"]
