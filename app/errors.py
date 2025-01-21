from typing import Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class DogyException(Exception):
    """Base class for all exceptions raised by Dogy."""
    def __init__(self, message: str = "Service is unavailable."):
        self.message = message
        super().__init__(self.message)

class InitialDetail(BaseModel):
    """Initial detail for error responses."""
    message: str
    error_code: str

class UserNotFound(DogyException):
    """Raised when a user is not found."""
    pass

class UserAlreadyExists(DogyException):
    """Raised when a user already exists."""
    pass

class PlaceNotFound(DogyException):
    """Raised when a place is not found."""
    pass

class PlaceAlreadyExists(DogyException):
    """Raised when a place already exists."""
    pass

class PetNotFound(DogyException):
    """Raised when a pet is not found."""
    pass

class PetAlreadyExists(DogyException):
    """Raised when a pet already exists."""
    pass

class InvalidHexColorCode(DogyException):
    """Raised when an invalid hex code is given for a color."""
    pass

class InvalidEmail(DogyException):
    """Raised when an invalid email is given."""
    pass

class InputEmptyError(DogyException):
    """Raised when an input is empty."""
    pass

class NoBearerToken(DogyException):
    """Raised when no bearer token is given."""
    pass

class InvalidCredentials(DogyException):
    """Raised when invalid credentials are given (bearer token)."""
    pass

def create_exception_handler(
    status_code: int, initial_detail: InitialDetail, headers: dict | None = None
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: DogyException):
        return JSONResponse(
            content=initial_detail.model_dump(),
            status_code=status_code,
            headers=headers
        )

    return exception_handler # type: ignore

def register_all_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=InitialDetail(
                message = "User not found.",
                error_code = "user_not_found"
            )
        )
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail=InitialDetail(
                message = "User already exists.",
                error_code = "user_exists"
            )
        )
    )

    app.add_exception_handler(
        PlaceNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=InitialDetail(
                message = "Place not found.",
                error_code = "place_not_found"
            )
        )
    )

    app.add_exception_handler(
        InputEmptyError,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail=InitialDetail(
                message = "Input parameter cannot be empty.",
                error_code = "input_empty"

            )
        )
    )

    app.add_exception_handler(
        NoBearerToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=InitialDetail(
                message = "Not authorized. No bearer token provided.",
                error_code = "no_bearer_token"
            ),
            headers={"WWW-Authenticate": "Bearer"}
        )
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=InitialDetail(
                message = "Invalid credentials. Please provide a valid bearer token.",
                error_code = "invalid_credentials"
            ),
            headers={"WWW-Authenticate": "Bearer"}
        )
    )

