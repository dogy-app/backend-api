from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.core import get_session
from app.pets.crud import PetService
from app.pets.schemas import PetCreate, PetResponse

router = APIRouter()
pet_service = PetService()

@router.post("/", response_model=PetResponse)
async def create_pet(pet: PetCreate, db: AsyncSession = Depends(get_session)):
    pet_created = await pet_service.create_pet(session=db, pet_req=pet)
    return pet_created

@router.get("/{pet_id}")
async def get_pet_by_id(pet_id: UUID, db: AsyncSession = Depends(get_session)):
    pet = await pet_service.get_pet_by_id(session=db, pet_id=pet_id)
    return pet
#
# @router.delete("/")
# def delete_pet(pet_uuid: UUID, db: Session = Depends(get_session)):
#     pet_service.delete_pet(pet_uuid)
#     return { "status": "success" }
