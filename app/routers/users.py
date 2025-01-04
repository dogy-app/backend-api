from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.core import get_session
from app.database.models import User
from app.users.crud import UserRepository

router = APIRouter(prefix="/user")

@router.post("/", response_model=User)
def create_user(user: User, db: Session = Depends(get_session)):  
    user_repo = UserRepository(session=db)
    user_created = user_repo.create_user(user)
    return user_created

@router.get("/{user_uuid}", response_model=User)
def get_user_by_uuid(user_uuid: str, db: Session = Depends(get_session)):
    user_repo = UserRepository(session=db)
    user = user_repo.get_user_by_id(user_uuid)
    return user

@router.delete("/")
def delete_user(user_uuid: UUID, db: Session = Depends(get_session)):
    user_repo = UserRepository(session=db)
    user_repo.delete_user(user_uuid)
    return { "status": "success" }
