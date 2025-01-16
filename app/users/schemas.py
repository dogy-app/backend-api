from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from pydantic.json_schema import SkipJsonSchema

from app.database.datatypes import AgeGroup, Gender, SubscriptionType


class UserSubscriptionRead(BaseModel):
    trial_start_date: date = Field(
        default_factory=date.today,
        description="Date the user started the trial."
    )
    subscription_type: SubscriptionType = Field(
        description="Type of subscription the user has"
    )
    is_registered: bool = Field(
        default=False,
        description="Whether the user has registered for the app."
    )
    is_trial_mode: bool = Field(
        default=False,
        description="Whether the user is in trial mode for premium."
    )

class UserPhotoRead(BaseModel):
    photo_url: str | None = Field(
        default=None,
        description="URL of the user's profile photo."
    )
    no_photo_color: str | None = Field(
        default=None,
        description="Color to use for the no photo icon. Must be a valid hex color code.",
    )
    no_photo_icon_str: str | None = Field(
        default=None,
        description="Placeholder letter/s to use when no photo is available."
    )

    @field_validator("no_photo_color")
    def validate_color(cls, value):
        if not value.startswith('#'):
            raise ValueError("Color must start with '#'.")
        if len(value) != 7:
            raise ValueError("Color must be exactly 7 characters long.")
        return value

class UserResponse(BaseModel):
    id: UUID
    name: str = Field(description="Full name of the user.")
    email: str = Field(description="Email address associated with Firebase.")
    gender: Gender
    age_group: AgeGroup
    has_onboarded: bool = Field(
            default=False,
            description="Whether the user has completed the onboarding process."
    )
    timezone: str = Field(description="Timezone of the user.")
    photo: UserPhotoRead
    subscription: UserSubscriptionRead

class UserCreate(UserResponse):
    id: SkipJsonSchema[int] = Field(default=1, exclude=True) # type: ignore
