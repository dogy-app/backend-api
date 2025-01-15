"""
Database Schema for PostgreSQL.
Schema version: 0.1.0
"""

import re
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import RelationshipProperty, declared_attr
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
        sa_relationship=RelationshipProperty(
            "PlaceMetadata",
            back_populates="place",
            uselist=False,
        )
    )

class PlaceMetadata(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    city: str | None = None
    country: str | None = None
    full_address: str | None = None
    place_id: UUID | None = Field(default=None, foreign_key="places.id", unique=True)
    place: Place | None = Relationship( # One-to-one relationship
        sa_relationship=RelationshipProperty(
            "Place",
            back_populates="place_metadata",
        )
    )


class UserPetLink(SQLModel, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id", primary_key=True)
    pet_id: UUID | None = Field(default=None, foreign_key="pet.id", primary_key=True)
    purpose: str | None = None
    role: UserRole | None = None


class User(TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None = None
    email: str | None = None
    gender: Gender | None = None
    age_group: AgeGroup | None = None
    user_photo: Optional["UserPhotoProp"] = Relationship(
        sa_relationship=RelationshipProperty(
            "UserPhotoProp",
            back_populates="user",
            uselist=False,
        )
    )
    user_subscription: Optional["UserSubscription"] = Relationship(
        sa_relationship=RelationshipProperty(
            "UserSubscription",
            back_populates="user",
            uselist=False,
        )
    )
    has_onboarded: bool = Field(default=False)
    timezone: str | None = None
    pets: list["Pet"] = Relationship(back_populates="owners", link_model=UserPetLink)

class UserPhotoProp(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, nullable=False)
    user_id: UUID | None = Field(default=None, foreign_key="user.id", unique=True)
    user: User | None = Relationship(
        sa_relationship=RelationshipProperty(
            "User",
            back_populates="user_photo",
            uselist=False
        )
    )
    photo_url: str | None = None
    no_photo_color: str | None = Field(default=None, max_length=7)
    no_photo_icon_str: str | None = None

class UserSubscription(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(default=None, foreign_key="user.id", unique=True)
    user: User | None = Relationship(
        sa_relationship=RelationshipProperty(
            "User",
            back_populates="user_subscription",
            uselist=False
        )
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
    weight: Decimal = Field(default=0, max_digits=5, decimal_places=2)

class PetAttr(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_id: UUID | None = Field(default=None, foreign_key="pet.id")
    breeds: list["PetAttrBreed"] = Relationship(back_populates="pet_attr")
    aggression_level: list["PetAttrAggressionLevel"] = Relationship(back_populates="pet_attr")
    allergies: list["PetAttrAllergy"] = Relationship(back_populates="pet_attr")
    behaviors: list["PetAttrBehavior"] = Relationship(back_populates="pet_attr")
    interactions: list["PetAttrInteraction"] = Relationship(back_populates="pet_attr")
    personalities: list["PetAttrPersonality"] = Relationship(back_populates="pet_attr")
    reactivity: list["PetAttrReactivity"] = Relationship(back_populates="pet_attr")
    sterilised: bool | None = None

class PetAttrBreed(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="breeds")
    breed: PetBreed

class PetAttrAggressionLevel(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="aggression_level")
    aggression_level: PetAggressionLevel

class PetAttrAllergy(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="allergies")
    allergy: PetAllergy

class PetAttrBehavior(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="behaviors")
    behavior: PetBehavior

class PetAttrInteraction(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="interactions")
    interaction: PetInteraction

class PetAttrPersonality(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="personalities")
    personality: PetPersonality

class PetAttrReactivity(SQLModel, table=True):
    __tablename__ = declared_attr(lambda cls: to_snake_case(cls.__name__)) # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pet_attr_id: UUID | None = Field(default=None, foreign_key="pet_attr.id")
    pet_attr: Optional["PetAttr"] = Relationship(back_populates="reactivity")
    reactivity: PetReactivity
