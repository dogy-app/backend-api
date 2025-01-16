from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.pydantic import filter_fields
from app.database.models import User, UserPhotoProp, UserSubscription

from .schemas import UserCreate


class UserRepository:
    async def create_user(self, user_req: UserCreate, session: AsyncSession) -> User:
        # User
        user_data = filter_fields(User, user_req)
        user = User.model_validate(user_data)

        # UserSubscription
        user_subscription_data = filter_fields(UserSubscription, user_req)
        user_subscription = UserSubscription.model_validate(user_subscription_data)

        # UserPhotoProp
        user_photo_prop_data = filter_fields(UserPhotoProp, user_req)
        user_photo_prop = UserPhotoProp.model_validate(user_photo_prop_data)

        # Relationships
        user.user_subscription = user_subscription
        user.user_photo = user_photo_prop

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: UUID, session: AsyncSession) -> User:
        user = await session.get(User, user_id)
        if user is None:
            raise Exception("User not found")
        return user

    async def delete_user(self, user_id: UUID, session: AsyncSession) -> None:
        user = await session.get(User, user_id)
        if user is None:
            raise Exception("User not found")
        await session.delete(user)
        await session.commit()
        return None
