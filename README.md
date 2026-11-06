# Takehome challenge

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/Razihel92/takehome-challenge-python/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/Razihel92/takehome-challenge-python/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/Razihel92/takehome-challenge-python/badge.svg?branch=main)](https://coveralls.io/github/Razihel92/takehome-challenge-python?branch=main)

### Live demo

Interactive API docs [API Swagger](https://takehome-challenge-python.onrender.com/docs)

> Hosted on Render's free tier: the service sleeps when idle, so the first request may take ~30-50 seconds to wake it up.

Deployed on **Render** (Docker) with a **Neon** PostgreSQL database. Every push to `main` runs the CircleCI pipeline, and Render deploys automatically once the checks pass.

### Features

- Create new Users with their Pokemon Ids
- Get Users list
- Get User by Id and also gathering Pokemon Names from Poke API
- Update User
- Delete User

---

## Stack

- **FastAPI** (Python 3.14)
- **PostgreSQL** + **SQLAlchemy 2 (async)** with `asyncpg`
- **Alembic** for migrations
- **httpx** to consume the [PokeAPI](https://pokeapi.co/)
- **pytest** for e2e tests
- **uv** as package manager

## Quick start (Docker)

Requires only Docker:

```bash
cp .env.example .env
docker compose up --build
```

This starts PostgreSQL, applies the migrations and runs the API at
`http://localhost:8080/docs`. Stop everything with `docker compose down`.

## Local development setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Env vars must be defined. Copy the example and adjust the values if needed:

   ```bash
   cp .env.example .env
   ```

3. Start the database:

   ```bash
   docker compose up -d db
   ```

4. Run the migrations:

   ```bash
   uv run alembic upgrade head
   ```

## Run the project

```bash
uv run fastapi dev app/main.py
```

Interactive docs are available at `http://localhost:8000/docs`.

## Endpoints

| Method   | Path              | Description                                    |
| -------- | ----------------- | ---------------------------------------------- |
| `POST`   | `/users/`         | Create a user with its Pokemon and item ids    |
| `GET`    | `/users/`         | List all users                                 |
| `GET`    | `/users/{id}`     | Get a user with Pokemon/item names from PokeAPI |
| `PATCH`  | `/users/{id}`     | Partially update a user                        |
| `DELETE` | `/users/{id}`     | Delete a user                                  |

### Error responses

| Status | When                                                 |
| ------ | ---------------------------------------------------- |
| `400`  | One or more Pokemon/item ids don't exist in PokeAPI  |
| `404`  | The user doesn't exist                               |
| `409`  | The username or email is already in use              |
| `422`  | The request body doesn't match the expected schema   |

## Run tests

Tests run against a separate PostgreSQL instance (`db_test`, port `5434`) and mock
PokeAPI at the HTTP level, so no internet connection is needed.

1. Copy the test env vars (they already match the `db_test` service in
   `docker-compose.yaml`):

   ```bash
   cp .env.test.example .env.test
   ```

   `APP_ENV=test` is required: the test suite refuses to run against any other
   database, since it truncates tables between tests.

2. Start the test database (`--wait` returns once PostgreSQL is ready to
   accept connections):

   ```bash
   docker compose up -d --wait db_test
   ```

3. Run the suite:

   ```bash
   uv run pytest -v
   ```

## Decisions made

- **Layered architecture (router → service → repository):** each layer has one
  job. Routers handle HTTP, services hold the business rules (PokeAPI
  validation, 404 errors) and repositories talk to the database (and turn
  unique-constraint violations into 409). This
  makes future changes easier, like swapping the database or adding an
  endpoint, without touching the other layers.
- **FastAPI:** async by default, request/response validation with Pydantic and
  interactive docs (`/docs`) out of the box.
- **SQLAlchemy 2 (async) + Alembic:** SQLAlchemy is the most widely used ORM
  in Python, so fixes and people who know it are easy to find. Alembic
  versions the schema so every environment gets the same tables.
- **httpx:** async HTTP client to call PokeAPI. Requests for several ids run
  concurrently and repeated ids are fetched only once.
- **Docker:** to make the project portable. One command starts the database,
  applies the migrations and runs the API.
- **uv:** fast package manager with a lockfile (`uv.lock`), so everyone installs
  exactly the same versions.
- **pytest / E2E testing:** pytest is the most used testing framework in Python.
  Tests are end-to-end: they call the real endpoints against a real PostgreSQL
  database (`db_test`), and only PokeAPI is mocked at the HTTP level. If an
  endpoint returns the right response, every layer behind it works, so there
  is no need to test each part in isolation.
