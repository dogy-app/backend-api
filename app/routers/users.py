from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi_clerk_auth import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.errors import InternalUserNotFound, NotAuthorized, UserNotFound
from app.users.auth import clerk_auth_guard, get_role_from_auth, get_user_id_from_auth
from app.users.crud import UserCreate, UserService
from app.users.responses import (
    Status,
    UserDeletedResponse,
    user_delete_responses,
    user_get_responses,
    user_post_responses,
)

router = APIRouter()
user_service = UserService()

@router.get("/test/{user_id}") # type: ignore
async def get(
        user_id: str,
        db: Annotated[AsyncSession, Depends(get_session)]
    ):
    user_created = await user_service.get_user_id_from_external_id(session=db,external_id=user_id)
    return user_created

@router.post("/", responses=user_post_responses) # type: ignore
async def create_user(
        user: UserCreate,
        user_id: Annotated[str, Depends(get_user_id_from_auth)],
        role: Annotated[str, Depends(get_role_from_auth)],
        db: Annotated[AsyncSession, Depends(get_session)]
    ):
    if (role != "org:admin" or role is None) and user_id != user.external_id:
        raise NotAuthorized("You are not authorized to create another user.")
    user_created = await user_service.create_user(session=db, user_req=user)
    return user_created

# Test Route
@router.get("/auth", summary="Authenticate users") # type: ignore
def auth_user(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    user_id = get_user_id_from_auth(credentials)
    return {"user_id": user_id}

@router.get("/me", responses=user_get_responses, summary="Get User By ID") # type: ignore
async def get_user_by_id(
        db: Annotated[AsyncSession, Depends(get_session)],
        user_id: Annotated[str, Depends(get_user_id_from_auth)]
    ):
    internal_id = await user_service.get_user_id_from_external_id(session=db,external_id=user_id)

    try:
        user = await user_service.get_user_by_id(session=db, user_id=internal_id)
    except InternalUserNotFound:
        raise UserNotFound("User not found.")
    return user

@router.get("/{user_id}", responses=user_get_responses, summary="Get User By ID (Admin)") # type: ignore
async def get_user_by_id_(
        db: Annotated[AsyncSession, Depends(get_session)],
        role: Annotated[str, Depends(get_role_from_auth)],
        user_id: Annotated[str, Path(description="Clerk user ID", min_length=32, max_length=32)]
    ):
    if role != "org:admin" or role is None:
        raise NotAuthorized("You are not authorized to access this user.")

    internal_id = await user_service.get_user_id_from_external_id(session=db,external_id=user_id)
    try:
        user = await user_service.get_user_by_id(session=db, user_id=internal_id)
    except InternalUserNotFound:
        raise UserNotFound("User not found.")
    return user

@router.delete("/{user_id}", responses=user_delete_responses) # type: ignore
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_session)],
        role: Annotated[str, Depends(get_role_from_auth)],
        user_id: Annotated[str, Path(description="Clerk user ID", min_length=32, max_length=32)]
    ):
    if role != "org:admin" or role is None:
        raise NotAuthorized("You are not authorized to delete this user.")

    internal_id = await user_service.get_user_id_from_external_id(session=db,external_id=user_id)
    try:
        await user_service.delete_user(session=db, user_id=internal_id)
    except InternalUserNotFound:
        raise UserNotFound("User not found.")
    return UserDeletedResponse(status=Status.success)
