from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.pydantic import filter_fields
from app.database.models import User, UserPhotoProp, UserSubscription

from .schemas import UserCreate, UserPhotoRead, UserResponse, UserSubscriptionRead


class UserRepository:
    async def create_user(self, user_req: UserCreate, session: AsyncSession) -> UserResponse:
        user = User(**filter_fields(User, user_req))
        user.photo = UserPhotoProp(**filter_fields(UserPhotoRead, user_req.photo))
        user.subscription = UserSubscription(
            **filter_fields(UserSubscriptionRead, user_req.subscription)
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        response = UserResponse(
            **user.model_dump(),
            subscription=user_req.subscription,
            photo=user_req.photo
        )
        return response

    async def get_user_by_id(self, user_id: UUID, session: AsyncSession) -> UserResponse:
        user_full = (select(User, UserPhotoProp, UserSubscription)
        .join(UserPhotoProp)
        .join(UserSubscription)
        .where(User.id == user_id))

        result = await session.exec(user_full)
        user, user_photo_prop, user_subscription = result.one_or_none() # type: ignore
        if user or user_photo_prop or user_subscription is None:
            raise Exception("User not found")
        response = UserResponse(
            **user.model_dump(exclude={"created_at", "updated_at", "deleted_at"}),
            subscription=UserSubscriptionRead(
                **user_subscription.model_dump(exclude={"user_id"})
            ),
            photo=UserPhotoRead(**user_photo_prop.model_dump(exclude={"user_id"}))
        )

        return response

    async def delete_user(self, user_id: UUID, session: AsyncSession) -> None:
        user = await session.get(User, user_id)
        if user is None:
            raise Exception("User not found")
        await session.delete(user)
        await session.commit()
        return None
