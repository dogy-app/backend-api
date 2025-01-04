from uuid import UUID

from sqlmodel import Session, select

from app.database.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> User:
        if not user_id:
            raise Exception("User ID is required")
        query = select(User).where(User.user_id == user_id)
        results = self.session.exec(query)
        if not results:
            raise Exception("User not found")
        user = results.first()
        if not user:
            raise Exception("User not found")
        return user

    def delete_user(self, user_id: UUID) -> None:
        user = self.session.get(User, user_id)
        self.session.delete(user)
        self.session.commit()
        return None
