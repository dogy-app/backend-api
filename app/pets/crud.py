from pprint import pprint
from typing import Tuple
from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.pydantic import filter_fields
from app.database.datatypes import UserRole
from app.database.models import (
    PET_ATTR_MODEL_MAPPING,
    Pet,
    PetAttr,
    User,
    UserPetLink,
)
from app.database.utils import flatten_list_to_entries
from app.errors import InternalPetNotFound, InternalUserNotFound
from app.users.crud import UserService

from .schemas import PetAttrRead, PetCreate, PetResponse

user_service = UserService()

class PetService:
    async def link_pet_to_user(
            self,
            session: AsyncSession,
            pet: Pet,
            user_id: UUID,
            role: UserRole
    ) -> Tuple[User, str | None, UserPetLink]:
        user = await session.get(User, user_id)
        if not user:
            raise InternalUserNotFound

        link = UserPetLink(user=user, pet=pet, role=role)

        # FIXME: External ID cannot be passed outside the function, so external
        # ID is included in the return tuple.
        return (user, user.external_id, link)

    async def add_links(self, session: AsyncSession, user: User, link:
                        UserPetLink) -> None:
        # FIXME: Support for linking to existing users (append()). Issue here is
        # that user.pet_links doesn't exist initially.

        session.add(link)
        # user.pet_links.append(link)
        # session.add(user)

    async def create_pet(self, session: AsyncSession, pet_req: PetCreate) -> PetResponse:
        pet = Pet(**filter_fields(Pet, pet_req))
        pet_attr = PetAttr(sterilized=pet_req.attributes.sterilized)  # type: ignore

        flatten_list_to_entries(
            input_model=pet_req.attributes,
            output_model=pet_attr,
            mapping=PET_ATTR_MODEL_MAPPING
        )

        pet.attributes = pet_attr
        user, external_id, user_pet_link = await self.link_pet_to_user(
            session,
            pet,
            pet_req.user_id,
            pet_req.role
        )

        try:
            session.add(pet)
            await self.add_links(session, user, user_pet_link)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise Exception("Pet already exists")
        await session.refresh(pet)
        await session.refresh(pet_attr)

        response = PetResponse(
            **pet.model_dump(),
            attributes=pet_req.attributes,
            user_id=external_id # type: ignore
        )

        return response

    async def get_pet_by_id(
            self,
            session: AsyncSession,
            pet_id: UUID,
            user_id: str | None = None
    ) -> PetResponse:
        query = (select(Pet, PetAttr, UserPetLink)
        .join(PetAttr)
        .join(UserPetLink)
        .where(Pet.id == pet_id)
        )

        try:
            result = await session.exec(query)
            pet, pet_attr, user_pet_link = result.one()
        except NoResultFound:
            raise InternalPetNotFound(f"Pet {pet_id} not found.")

        if user_id:
            external_id = user_id
        else:
            external_id = await user_service.get_user_id_from_internal_id(
                session=session,
                internal_id=user_pet_link.user_id # type: ignore
            )

        pprint(f"Breed: {pet_attr}")

        response = PetResponse(
            **pet.model_dump(exclude={"created_at", "updated_at"}),
            attributes=PetAttrRead(
                **pet_attr.model_dump()
            ),
            role=user_pet_link.role,
            user_id=external_id # type: ignore
        )

        return response
    #
    # def delete_pet(self, pet_id: UUID) -> None:
    #     pet = self.session.get(Pet, pet_id)
    #     self.session.delete(pet)
    #     self.session.commit()
    #     return None
