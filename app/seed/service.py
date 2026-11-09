from fastapi import Depends

from app.seed.data import SEED_USERS
from app.users.repository import UserRepository
from app.users.schemas import UserResponseSchema
from app.users.service import UserService


class SeedService:
    def __init__(
        self,
        repository: UserRepository = Depends(UserRepository),
        service: UserService = Depends(UserService),
    ) -> None:
        self.repository = repository
        self.service = service

    async def run_seed(self) -> list[UserResponseSchema]:
        await self.repository.delete_all_users()
        created_users = [await self.service.create_user(user) for user in SEED_USERS]
        return created_users
