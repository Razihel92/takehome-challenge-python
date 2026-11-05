from pydantic import BaseModel


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    pokemon_ids: list[int] | None = None
    items_ids: list[int] | None = None
