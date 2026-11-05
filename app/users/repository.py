from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import AppError
from app.users.models import User
from app.users.schemas import UserCreateSchema, UserUpdateSchema


class UserRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create_user(self, user_data: UserCreateSchema) -> User:
        new_user = User(**user_data.model_dump())
        self.db.add(new_user)
        await self._commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_all_users(self) -> list[User]:
        resultado = await self.db.execute(select(User).order_by(User.id))
        return list(resultado.scalars().all())

    async def update_user(
        self, user_id: int, user_data: UserUpdateSchema
    ) -> User | None:
        user = await self.db.get(User, user_id)
        if user is None:
            return None
        for key, value in user_data.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(user, key, value)
        await self._commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> User | None:
        user_to_delete = await self.get_user_by_id(user_id)
        if user_to_delete is None:
            return None
        await self.db.delete(user_to_delete)
        await self.db.commit()
        return user_to_delete

    async def _commit(self) -> None:
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise AppError.conflict("El username o email ya está en uso") from exc
