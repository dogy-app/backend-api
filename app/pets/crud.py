from uuid import UUID

from sqlmodel import Session, select

from app.database.models import Pet


class PetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def create_pet(self, pet: Pet) -> Pet:
        self.session.add(pet)
        self.session.commit()
        self.session.refresh(pet)
        return pet

    def get_pet_by_id(self, pet_id: str) -> Pet:
        if not pet_id:
            raise Exception("Pet ID is required")
        query = select(Pet).where(Pet.pet_id == pet_id)
        results = self.session.exec(query)
        if not results:
            raise Exception("Pet not found")
        pet = results.first()
        if not pet:
            raise Exception("Pet not found")
        return pet

    def delete_pet(self, pet_id: UUID) -> None:
        pet = self.session.get(Pet, pet_id)
        self.session.delete(pet)
        self.session.commit()
        return None
