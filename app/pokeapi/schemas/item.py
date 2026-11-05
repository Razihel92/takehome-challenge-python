from typing import ClassVar

from pydantic import BaseModel


class ItemSchema(BaseModel):
    DISPLAY_NAME: ClassVar[str] = "Item"

    id: int
    name: str
