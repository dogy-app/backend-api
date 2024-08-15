import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class PlaceBase(SQLModel):
    name: str
    latitude: Decimal = Field(default=0, max_digits=7, decimal_places=4)
    longitude: Decimal = Field(default=0, max_digits=7, decimal_places=4)
    website_url: Optional[str] = None


class Park(PlaceBase, table=True):
    __tablename__ = "parks"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    gmaps_id: str
    city: str
    country: str
    geohash: str
    address: str
    image: Optional[str] = None
    visited_by: List[str] = Field(sa_column=Column(JSON))

    class Config:
        arbitrary_types_allowed = True


# class Playtime(SQLModel, table=True):
#     __tablename__ = "playtimes"
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     created_at: datetime
#     park_id: str = Field(default=None, foreign_key="parks.gmaps_id")
#     park_name: str
#     playtime: str
#     playtime_date: str
#     status: str
#     user_ids: List[str]


# class PlaytimeReminder(SQLModel):
#     hour: int
#     minute: int
#     title: str
#     subtitle: Optional[str] = None
#     message: str
#     pet_name: str


# class Pet(SQLModel, table=True):
#     __tablename__ = "pets"
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     pet_id: str
#     created_at: datetime
#     name: str
#     agression_level: List[str]
#     behaviour: List[str]
#     birthday: str
#     breed: str
#     interaction: List[str]
#     owners: List["User"] = Relationship(back_populates="pets")
#     personalities: List[str]
#     photo_url: Optional[str] = None
#     reactivity: List[str]
#     sex: str
#     size: str
#     sterilised: str
#     traits: str
#     weight: int


# class UserParkLink(SQLModel, table=True):
#     __tablename__ = "user_park_link"
#     user_id: str = Field(foreign_key="users.user_id", primary_key=True)
#     park_id: str = Field(foreign_key="parks.gmaps_id", primary_key=True)


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime
    user_id: str
    name: str
    email: str
    gender: str
    age_group: str
    dogy_notification: bool
    daily_notification: bool
    # daily_playtime_reminder: PlaytimeReminder
    park_notification: bool
    has_onboarded: bool
    notifications_enabled: bool
    last_notification_sent: datetime
    purpose: str
    photo_url: Optional[str] = None
    # push_ids: List[str] = Field(sa_column=Column(ARRAY(String), nullable=True))
    # pets: List[Pet] = Relationship(back_populates="owners")
    role: str
    timezone: str
    total_pets: int = 0
    # visited_parks: List[Park] = Relationship(
    #     back_populates="visited_by", link_model=UserParkLink
    # )
