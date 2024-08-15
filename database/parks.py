from sqlmodel import Session

from .models import Park


def create_parks(*, session: Session, parks: list[Park]):
    session.add_all(parks)
    session.commit()
    print("Parks added successfully")
    return parks
