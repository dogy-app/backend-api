from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import ARRAY, Column, Field, Relationship, SQLModel, String

from .datatypes import *
from .mixins.geolocation import GeolocationMixin
from .mixins.timestamp import TimestampMixin


# Models
class PlaceBase(TimestampMixin, GeolocationMixin):
    name: str
    description: str | None = None
    type: str

class Place(PlaceBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    gmaps_id: str | None = None
    images: list[str] = Field(sa_column=Column(ARRAY(String), nullable=True))
    website_url: str | None = None
    location_metadata_id: UUID | None = Field(default=None, foreign_key="location_metadata.id")
    location_metadata: Optional["LocationMetadata"] = Relationship(back_populates="place")

class LocationMetadata(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    city: str | None = None
    country: str | None = None
    geohash: str | None = Field(max_length=12)
    address: str | None = None
    place: Place | None = Relationship( # One-to-one relationship
        sa_relationship_kwargs={"uselist": False},
        back_populates="location_metadata"
    )


class UserPetLink(SQLModel, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id", primary_key=True)
    pet_id: UUID | None = Field(default=None, foreign_key="pet.id", primary_key=True)


class User(TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(unique=True)
    name: str | None = None
    email: str | None = None
    gender: GenderEnum | None = None
    age_group: AgeGroupEnum | None = None
    user_photo_id: UUID | None = Field(default=None, foreign_key="userphotoprop.id")
    user_photo: Optional["UserPhotoProp"] = Relationship(back_populates="user")
    has_onboarded: bool = Field(default=False)
    purpose: str | None = None
    role: RoleEnum | None = None
    timezone: str | None = None
    pets: list["Pet"] = Relationship(back_populates="owners", link_model=UserPetLink)

class UserPhotoProp(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user: User | None = Relationship(
        sa_relationship_kwargs={"uselist": False},
        back_populates="user_photo"
    )
    photo_url: str | None = None
    no_photo_color: str | None = Field(default=None, max_length=7)
    no_photo_icon_str: str | None = None


class Pet(TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_id: str = Field(unique=True)
    name: str | None = None
    birthday: date | None
    photo_url: str | None = None
    sex: GenderEnum | None = None
    owners: list["User"] = Relationship(back_populates="pets", link_model=UserPetLink)
    photo_url: str | None = None
    size: PetSizeEnum | None = None
    weight: Decimal = Field(default=0, max_digits=5, decimal_places=2)

class PetAttr(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    breed: str | None = None
    agression_level: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    behaviour: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    interaction: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    personalities: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    reactivity: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    sterilised: bool | None = None


def validate_schema_place(example):
    example_instance = Place.model_validate(example)
    print(example_instance.model_dump_json(indent=4))
    print(example_instance.model_json_schema())
