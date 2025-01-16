from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.database.datatypes import AgeGroup, Gender, SubscriptionType


class UserBaseCreate(BaseModel):
    name: str = Field(description="Full name of the user")
    email: str = Field(description="Email address associated with Firebase")
    gender: Gender
    age_group: AgeGroup
    has_onboarded: bool = Field(
            default=False,
            description="Whether the user has completed the onboarding process"
    )
    timezone: str = Field(description="Timezone of the user.")

class UserSubscriptionCreate(BaseModel):
    trial_start_date: date = date.today()
    subscription_type: SubscriptionType
    is_registered: bool
    is_trial_mode: bool

class UserPhotoPropCreate(BaseModel):
    photo_url: str | None = None
    no_photo_color: str | None = None
    no_photo_icon_str: str | None = None

    @field_validator("no_photo_color")
    def validate_color(cls, value):
        if not value.startswith('#'):
            raise ValueError("Color must start with '#'")
        if len(value) != 7:
            raise ValueError("Color must be exactly 7 characters long")
        return value

class UserCreate(UserBaseCreate, UserSubscriptionCreate, UserPhotoPropCreate):
    pass

class UserResponse(UserCreate):
    id: UUID
