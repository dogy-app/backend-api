from datetime import datetime
from typing import Optional

from sqlmodel import ARRAY, Column, Field, Relationship, SQLModel, String

from .mixins.geolocation import GeolocationMixin
from .mixins.timestamp import TimestampMixin


class PlaceBase(TimestampMixin, GeolocationMixin):
    name: str
    description: str | None = None
    type: str


class UserPlaceLink(TimestampMixin, table=True):
    __tablename__ = "usersplaceslink"
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
    places_id: int | None = Field(
        default=None, foreign_key="places.id", primary_key=True
    )
    comment: str | None = None
    rating: int | None = None


class UserPlaytimeLink(SQLModel, table=True):
    __tablename__ = "usersplaytimeslink"
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
    playtime_id: int | None = Field(
        default=None, foreign_key="playtimes.id", primary_key=True
    )


class UserPetLink(SQLModel, table=True):
    __tablename__ = "userspetslink"
    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
    pet_id: int | None = Field(default=None, foreign_key="pets.id", primary_key=True)


class Place(PlaceBase, table=True):
    __tablename__ = "places"
    id: int | None = Field(default=None, primary_key=True)
    gmaps_id: str | None = None
    city: str | None = None
    country: str | None = None
    geohash: str | None = None
    address: str | None = None
    images: list[str] = Field(sa_column=Column(ARRAY(String), nullable=True))
    website_url: str | None = None
    visited_by: list["User"] = Relationship(
        back_populates="visited_places", link_model=UserPlaceLink
    )


class User(TimestampMixin, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    user_id: str | None = None
    notification_id: int | None = Field(default=None, foreign_key="notifications.id")
    notification: Optional["Notification"] = Relationship(back_populates="user")
    playtimes: list["Playtime"] | None = Relationship(
        back_populates="users", link_model=UserPlaytimeLink
    )
    name: str | None = None
    email: str | None = None
    gender: str | None = None
    age_group: str | None = None
    daily_playtime_reminder: int | None = Field(
        default=None, foreign_key="playtime_reminders.id"
    )
    playtime_reminder: Optional["PlaytimeReminder"] = Relationship(
        back_populates="user"
    )
    has_onboarded: bool | None = None
    purpose: str | None = None
    photo_url: str | None = None
    pets: list["Pet"] = Relationship(back_populates="owners", link_model=UserPetLink)
    role: str | None = None
    timezone: str | None = None
    visited_places: list[Place] = Relationship(
        back_populates="visited_by", link_model=UserPlaceLink
    )


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: int | None = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(
        back_populates="notification", sa_relationship_kwargs={"uselist": False}
    )
    dogy_notification: bool | None = None
    daily_notification: bool | None = None
    park_notification: bool | None = None
    notifications_enabled: bool | None = None
    last_notification_sent: datetime | None = None
    push_ids: list[str] = Field(sa_column=Column(ARRAY(String), nullable=True))


class Playtime(SQLModel, table=True):
    __tablename__ = "playtimes"
    id: int | None = Field(default=None, primary_key=True)
    place_id: int | None = Field(default=None, foreign_key="places.id")
    playtime: datetime | None = None
    status: str | None = None
    users: list[User] | None = Relationship(
        back_populates="playtimes", link_model=UserPlaytimeLink
    )


class PlaytimeReminder(SQLModel, table=True):
    __tablename__ = "playtime_reminders"
    id: int | None = Field(default=None, primary_key=True)
    user: User | None = Relationship(back_populates="playtime_reminder")
    hour: int | None = None
    minute: int | None = None
    title: str | None = None
    subtitle: str | None = None
    message: str | None = None
    pet_id: int | None = Field(default=None, foreign_key="pets.id")
    pet: Optional["Pet"] = Relationship(back_populates="playtime_reminder")


class Pet(TimestampMixin, table=True):
    __tablename__ = "pets"
    id: int | None = Field(default=None, primary_key=True)
    pet_id: str | None = None
    name: str | None = None
    agression_level: list[str] | None = Field(
        sa_column=Column(ARRAY(String), nullable=True)
    )
    behaviour: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    birthday: str | None = None
    breed: str | None = None
    interaction: list[str] | None = Field(
        sa_column=Column(ARRAY(String), nullable=True)
    )
    owners: list["User"] = Relationship(back_populates="pets", link_model=UserPetLink)
    personalities: list[str] | None = Field(
        sa_column=Column(ARRAY(String), nullable=True)
    )
    photo_url: str | None = None
    playtime_reminder: Optional[PlaytimeReminder] = Relationship(
        back_populates="pet", sa_relationship_kwargs={"uselist": False}
    )
    reactivity: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True))
    sex: str | None = None
    size: str | None = None
    sterilised: str | None = None
    traits: str | None = None
    weight: int | None = None


def validate_schema_place(example):
    example_instance = Place.model_validate(example)
    print(example_instance.model_dump_json(indent=4))
    print(example_instance.model_json_schema())
