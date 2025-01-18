from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.users.crud import UserCreate, UserService
from app.users.responses import (
    Status,
    UserDeletedResponse,
    user_delete_responses,
    user_get_responses,
    user_post_responses,
)

router = APIRouter()
user_repo = UserService()

@router.post("/", responses=user_post_responses) # type: ignore
async def create_user(user: UserCreate,
                      db: Annotated[AsyncSession, Depends(get_session)]):
    user_created = await user_repo.create_user(session=db, user_req=user)
    return user_created

@router.get("/{user_id}", responses=user_get_responses, summary="Get User By Firebase UID") # type: ignore
async def get_user_by_firebase_uid(
        db: Annotated[AsyncSession, Depends(get_session)],
        user_id: Annotated[str, Path(description="Firebase UID associated with the user.",
                            min_length=28, max_length=28)]
    ):
    user = await user_repo.get_user_by_id(session=db, user_id=user_id)
    return user

@router.get("/internal/{user_id}", responses=user_get_responses, summary="Get User By User ID") # type: ignore
async def get_user_by_id(
        db: Annotated[AsyncSession, Depends(get_session)],
        user_id: Annotated[UUID, Path(description="User ID from the database.")]
    ):
    user = await user_repo.get_user_by_id(session=db, user_id=user_id)
    return user

@router.delete("/{user_id}", responses=user_delete_responses) # type: ignore
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_session)],
        user_id: Annotated[UUID, Path(description="User ID from the database.")]
    ):
    await user_repo.delete_user(session=db, user_id=user_id)
    return UserDeletedResponse(status=Status.success)
