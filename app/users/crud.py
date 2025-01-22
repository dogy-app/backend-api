from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.pydantic import filter_fields
from app.database.models import User, UserSubscription
from app.errors import (
    InputEmptyError,
    InternalUserNotFound,
    UserAlreadyExists,
    UserNotFound,
)

from .schemas import UserCreate, UserResponse, UserSubscriptionRead


class UserService:
    async def get_user_id_from_external_id(
        self,
        session: AsyncSession,
        external_id: str
    ):
        if len(external_id) == 0:
            raise InputEmptyError("User ID is required.")
        try:
            query = select(User.id).where(User.external_id == external_id)
            result = await session.exec(query)
            user_id = result.one()
        except NoResultFound:
            raise UserNotFound(f"User '{external_id}' does not exist.")
        return user_id

    async def create_user(self, session: AsyncSession, user_req: UserCreate) -> UserResponse:
        user = User(**filter_fields(User, user_req))
        user.subscription = UserSubscription(
            **filter_fields(UserSubscriptionRead, user_req.subscription)
        )

        try:
            session.add(user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise UserAlreadyExists(f"User '{user_req.external_id}' already exists.")

        await session.refresh(user)

        response = UserResponse(
            **user.model_dump(),
            subscription=user_req.subscription,
        )
        return response

    async def get_user_by_id(self, session: AsyncSession, user_id: UUID) -> UserResponse:
        user_full = select(User, UserSubscription).join(UserSubscription).where(User.id == user_id)

        try:
            result = await session.exec(user_full)
            user, user_subscription = result.one()
        except NoResultFound:
            raise InternalUserNotFound(f"User '{user_id}' not found")

        response = UserResponse(
            **user.model_dump(exclude={"created_at", "updated_at"}),
            subscription=UserSubscriptionRead(
                **user_subscription.model_dump(exclude={"user_id"})
            ),
        )

        return response

    async def delete_user(self, session: AsyncSession, user_id: UUID) -> None:
        user = await session.get(User, user_id)
        if user is None:
            raise InternalUserNotFound(f"User '{user_id}' not found")
        await session.delete(user)
        await session.commit()
        return None
