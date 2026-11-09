from fastapi import APIRouter, Depends, status

from app.seed.service import SeedService
from app.users.schemas import UserResponseSchema

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post(
    "/", response_model=list[UserResponseSchema], status_code=status.HTTP_201_CREATED
)
async def run_seed(
    service: SeedService = Depends(SeedService),
) -> list[UserResponseSchema]:
    return await service.run_seed()
