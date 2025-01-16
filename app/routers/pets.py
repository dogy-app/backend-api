from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.core import get_session
from app.database.models import Pet
from app.pets.crud import PetRepository

router = APIRouter()

@router.post("/")
def create_pet(pet: Pet, db: Session = Depends(get_session)):
    pet_repo = PetRepository(session=db)
    pet_created = pet_repo.create_pet(pet)
    return pet_created

@router.get("/{pet_id}")
def get_pet_by_id(pet_id: str, db: Session = Depends(get_session)):
    pet_repo = PetRepository(session=db)
    pet = pet_repo.get_pet_by_id(pet_id)
    return pet

@router.delete("/")
def delete_pet(pet_uuid: UUID, db: Session = Depends(get_session)):
    pet_repo = PetRepository(session=db)
    pet_repo.delete_pet(pet_uuid)
    return { "status": "success" }
