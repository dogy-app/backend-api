from enum import Enum
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.users.crud import UserCreate, UserRepository
from app.users.schemas import UserResponse

router = APIRouter()
user_repo = UserRepository()

class Status(str, Enum):
    success = "success"
    failure = "failure"

class UserDeletedResponse(BaseModel):
    status: Status

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    user_created = await user_repo.create_user(session=db, user_req=user)
    return user_created

@router.get("/{user_id}", response_model=UserResponse, summary="Get User By Firebase UID")
async def get_user_by_firebase_uid(
        db: AsyncSession = Depends(get_session),
        user_id: str = Path(description="Firebase UID", min_length=28, max_length=28)
    ):
    user = await user_repo.get_user_by_id(session=db, user_id=user_id)
    return user

@router.get("/internal/{user_id}", response_model=UserResponse, summary="Get User By User ID")
async def get_user_by_id(
        db: AsyncSession = Depends(get_session),
        user_id: UUID = Path(description="User ID from the database")
    ):
    user = await user_repo.get_user_by_id(session=db, user_id=user_id)
    return user

@router.delete("/{user_id}", response_model=UserDeletedResponse)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_session)):
    await user_repo.delete_user(session=db, user_id=user_id)
    return UserDeletedResponse(status=Status.success)
