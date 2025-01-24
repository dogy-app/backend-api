from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.database.datatypes import (
    Gender,
    PetAggressionLevel,
    PetAllergy,
    PetBehavior,
    PetBreed,
    PetInteraction,
    PetPersonality,
    PetReactivity,
    PetSize,
    UserRole,
)


class PetAttrRead(BaseModel):
    breeds: list[PetBreed] = []
    aggression_levels: list[PetAggressionLevel] = []
    allergies: list[PetAllergy] = []
    behaviors: list[PetBehavior] = []
    interactions: list[PetInteraction] = []
    personalities: list[PetPersonality] = []
    reactivities: list[PetReactivity] = []
    sterilized: bool = False

class PetResponse(BaseModel):
    user_id: str = Field(min_length=32, max_length=32)
    name: str
    birthday: date | None
    photo_url: str | None
    gender: Gender | None
    size: PetSize | None
    role: UserRole = UserRole.DOG_OWNER
    weight: Decimal = Field(default=Decimal(0.0), max_digits=5, decimal_places=2)
    attributes: PetAttrRead

class PetCreate(PetResponse):
    user_id: UUID # type: ignore
    pass
