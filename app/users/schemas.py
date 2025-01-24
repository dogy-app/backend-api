from datetime import date

from pydantic import BaseModel, Field

from app.database.datatypes import Gender, SubscriptionType


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

class UserResponse(BaseModel):
    external_id: str = Field(min_length=32, max_length=32,
                              description="Clerk UID of the user.")
    name: str = Field(description="Full name of the user.")
    gender: Gender
    has_onboarded: bool = Field(
            default=False,
            description="Whether the user has completed the onboarding process."
    )
    timezone: str = Field(description="Timezone of the user.")
    subscription: UserSubscriptionRead

class UserCreate(UserResponse):
    pass
