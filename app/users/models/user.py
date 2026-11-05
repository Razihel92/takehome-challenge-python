from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    pokemon_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), server_default="{}")
    items_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), server_default="{}")
