from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.users.crud import UserCreate, UserRepository
from app.users.schemas import UserResponse

router = APIRouter()
user_repo = UserRepository()

class Status(str, Enum):
    success = "success"
    failure = "failure"

@dataclass
class UserDeletedResponse:
    status: Status

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    user_created = await user_repo.create_user(user, session=db)
    return user_created

@router.get("/", response_model=UserResponse, summary="Get User By ID")
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_session)):
    user = await user_repo.get_user_by_id(user_id, session=db)
    return user

@router.delete("/", response_model=UserDeletedResponse)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_session)):
    await user_repo.delete_user(user_id, session=db)
    return UserDeletedResponse(status=Status.success)
