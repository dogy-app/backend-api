from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.pydantic import filter_fields
from app.database.models import User, UserPhotoProp, UserSubscription
from app.errors import UserAlreadyExists, UserNotFound

from .schemas import UserCreate, UserPhotoRead, UserResponse, UserSubscriptionRead


class UserRepository:
    async def create_user(self, session: AsyncSession, user_req: UserCreate) -> UserResponse:
        user = User(**filter_fields(User, user_req))
        user.photo = UserPhotoProp(**filter_fields(UserPhotoRead, user_req.photo))
        user.subscription = UserSubscription(
            **filter_fields(UserSubscriptionRead, user_req.subscription)
        )

        try:
            session.add(user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise UserAlreadyExists(f"User '{user_req.firebase_uid}' already exists.")

        await session.refresh(user)

        response = UserResponse(
            **user.model_dump(),
            subscription=user_req.subscription,
            photo=user_req.photo
        )
        return response

    async def get_user_by_id(
            self,
            session: AsyncSession,
            user_id: UUID | str
        ) -> UserResponse:
        query = (User.id == user_id) if isinstance(user_id, UUID) else (User.firebase_uid == user_id)

        user_full = (select(User, UserPhotoProp, UserSubscription)
        .join(UserPhotoProp)
        .join(UserSubscription)
        .where(query))

        try:
            result = await session.exec(user_full)
            user, user_photo_prop, user_subscription = result.one()
        except NoResultFound:
            raise UserNotFound(f"User '{user_id}' not found")

        response = UserResponse(
            **user.model_dump(exclude={"created_at", "updated_at", "deleted_at"}),
            subscription=UserSubscriptionRead(
                **user_subscription.model_dump(exclude={"user_id"})
            ),
            photo=UserPhotoRead(**user_photo_prop.model_dump(exclude={"user_id"}))
        )

        return response

    async def delete_user(self, session: AsyncSession, user_id: UUID) -> None:
        user = await session.get(User, user_id)
        if user is None:
            raise UserNotFound(f"User '{user_id}' not found")
        await session.delete(user)
        await session.commit()
        return None
