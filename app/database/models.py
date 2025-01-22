"""
Database Schema for PostgreSQL.
Schema version: 0.1.0
"""

import re
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import declared_attr
from sqlmodel import ARRAY, Column, Field, Relationship, SQLModel, String

from .datatypes import *
from .mixins.geolocation import GeolocationMixin
from .mixins.timestamp import TimestampMixin


# Convert Capital Case to snake_case
def to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

# Models
class PlaceBase(TimestampMixin, GeolocationMixin):
    pass

class Place(PlaceBase, table=True):
    """place table is already used by PostGIS extension, thus we need to use a
    different name."""
    __tablename__ = "places" # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    gmaps_id: str | None = Field(default=None, max_length=27)
    name: str
    description: str | None = None
    type: PlaceType
    images: list[str] = Field(sa_column=Column(ARRAY(String), nullable=True))
    website_url: str | None = None
    place_metadata: Optional["PlaceMetadata"] = Relationship( # One-to-one relationship
        sa_relationship_kwargs={"uselist": False},
        back_populates="place",
        cascade_delete=True,
    )

class PlaceMetadata(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    city: str | None = None
    country: str | None = None
    full_address: str | None = None
    place_id: UUID | None = Field(default=None, foreign_key="places.id",
                                  unique=True, ondelete="CASCADE")
    place: Place | None = Relationship(back_populates="place_metadata")


class UserPetLink(SQLModel, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id",
                                 primary_key=True, ondelete="CASCADE")
    pet_id: UUID | None = Field(default=None, foreign_key="pet.id",
                                primary_key=True, ondelete="CASCADE")
    role: UserRole | None = None

class User(TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None = None
    external_id: str | None = Field(default=None, unique=True, min_length=32,
                                     max_length=32, index=True)
    timezone: str | None = None
    gender: Gender | None = None
    has_onboarded: bool = Field(default=False)
    subscription: Optional["UserSubscription"] = Relationship(
        sa_relationship_kwargs={"uselist": False},
        back_populates="user",
        cascade_delete=True,
    )
    pets: list["Pet"] = Relationship(back_populates="owners", link_model=UserPetLink)

class UserSubscription(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(default=None, foreign_key="user.id",
                                 unique=True, ondelete="CASCADE")
    user: User | None = Relationship(
        sa_relationship_kwargs={"uselist": False},
        back_populates="subscription",
    )
    trial_start_date: date | None = None
    subscription_type: SubscriptionType | None = None
    is_registered: bool = Field(default=False)
    is_trial_mode: bool = Field(default=False)

class Pet(TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None = None
    birthday: date | None
    photo_url: str | None = None
    gender: Gender | None = None
    owners: list["User"] = Relationship(back_populates="pets", link_model=UserPetLink)
    size: PetSize | None = None
    weight: Decimal = Field(default=Decimal(0.0), max_digits=5, decimal_places=2)
    attributes: Optional["PetAttr"] = Relationship(
        sa_relationship_kwargs={"uselist": False},
        back_populates="pet",
        cascade_delete=True,
    )

class PetAttr(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet: Optional["Pet"] = Relationship(
        sa_relationship_kwargs={"uselist": False},
        back_populates="attributes"
    )
    pet_id: UUID | None = Field(default=None, foreign_key="pet.id", ondelete="CASCADE")
    breeds: list["PetAttrBreed"] = Relationship(back_populates="pet_attr",
                                                cascade_delete=True)
    aggression_levels: list["PetAttrAggressionLevel"] = Relationship(
            back_populates="pet_attr", cascade_delete=True)
    allergies: list["PetAttrAllergy"] = Relationship(back_populates="pet_attr",
                                                     cascade_delete=True)
    behaviors: list["PetAttrBehavior"] = Relationship(back_populates="pet_attr",
                                                      cascade_delete=True)
    interactions: list["PetAttrInteraction"] = Relationship(
            back_populates="pet_attr", cascade_delete=True)
    personalities: list["PetAttrPersonality"] = Relationship(
            back_populates="pet_attr", cascade_delete=True)
    reactivities: list["PetAttrReactivity"] = Relationship(
            back_populates="pet_attr", cascade_delete=True)
    sterilized: bool = False

class PetAttrBreed(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="breeds")
    breed: PetBreed

class PetAttrAggressionLevel(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="aggression_levels")
    aggression_level: PetAggressionLevel

class PetAttrAllergy(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="allergies")
    allergy: PetAllergy

class PetAttrBehavior(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="behaviors")
    behavior: PetBehavior

class PetAttrInteraction(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="interactions")
    interaction: PetInteraction

class PetAttrPersonality(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="personalities")
    personality: PetPersonality

class PetAttrReactivity(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id", ondelete="CASCADE")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="reactivities")
    reactivity: PetReactivity
