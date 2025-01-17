from datetime import date
from enum import Enum
from uuid import UUID

from fastapi import status
from pydantic import BaseModel

from app.common.pydantic import ResponseTemplate
from app.database.datatypes import AgeGroup, Gender, SubscriptionType
from app.errors import InitialDetail

from .schemas import UserPhotoRead, UserResponse, UserSubscriptionRead

"""Response Models"""
class UserAlreadyExistsResponse(InitialDetail):
    pass

class UserNotFoundResponse(InitialDetail):
    pass

class Status(str, Enum):
    success = "success"
    failure = "failure"

class UserDeletedResponse(BaseModel):
    status: Status = Status.success


"""Example of Response Models"""
user_already_exist_response = UserAlreadyExistsResponse(
    message="User 'AC3snUb69laJEbaa2e3Vcmd505Z2' already exists.",
    error_code="user_exists"
)

user_not_found_response = UserNotFoundResponse(
    message="User 'AC3snUb69laJEbaa2e3Vcmd505Z2' not found.",
    error_code="user_not_found"
)

user_created_response = UserResponse(
    id=UUID("94162e9f-30f8-49c6-8a0d-abd4974096ee"),
    firebase_uid="AC3snUb69laJEbaa2e3Vcmd505Z2",
    name="Dummy User",
    email="dummyemail@dogy.app",
    gender=Gender.MALE,
    age_group=AgeGroup.UNDER_18,
    has_onboarded=True,
    timezone="PHT",
    photo=UserPhotoRead(
        photo_url = None,
        no_photo_color = "#000000",
        no_photo_icon_str = "PG"
    ),
    subscription=UserSubscriptionRead(
        trial_start_date = date.today(),
        subscription_type = SubscriptionType.ACTIVE,
        is_registered = True,
        is_trial_mode = True
    )
)

user_deleted_response = UserDeletedResponse(status=Status.success)


"""Responses for each Routes"""

"""
POST /users
"""
user_post_responses = {
    **ResponseTemplate(
        status_code=status.HTTP_200_OK,
        model=UserResponse,
        description="Success",
        example=user_created_response
    ).model_dump(),
    **ResponseTemplate(
        status_code=status.HTTP_409_CONFLICT,
        model=UserAlreadyExistsResponse,
        description="User Already Exists Error",
        example=user_already_exist_response
    ).model_dump(),
}

"""
GET /users/{user_id}
GET /users/internal/{user_id}
"""
user_get_responses = {
    status.HTTP_200_OK: {**user_post_responses[status.HTTP_200_OK]}, #type: ignore
    **ResponseTemplate(
        status_code=status.HTTP_404_NOT_FOUND,
        model=UserNotFoundResponse,
        description="User Not Found Error",
        example=user_not_found_response
    ).model_dump(),
}


"""
DELETE /users/{user_id}
"""
user_delete_responses = {
    **ResponseTemplate(
        status_code=status.HTTP_200_OK,
        model=UserDeletedResponse,
        description="Success",
        example=user_deleted_response
    ).model_dump(),
}
