from fastapi import APIRouter, Depends, status

from app.users.schemas import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreateSchema, service: UserService = Depends(UserService)
):
    return await service.create_user(user_data)


@router.get("/", response_model=list[UserResponseSchema])
async def get_all_users(service: UserService = Depends(UserService)):
    return await service.get_all_users()


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user_by_id(user_id: int, service: UserService = Depends(UserService)):
    return await service.get_user_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    service: UserService = Depends(UserService),
):
    return await service.update_user(user_id, user_data)


@router.delete("/{user_id}", response_model=UserResponseSchema)
async def delete_user(user_id: int, service: UserService = Depends(UserService)):
    return await service.delete_user(user_id)
