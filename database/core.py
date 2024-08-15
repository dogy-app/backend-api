import os

from sqlmodel import Session, SQLModel, create_engine

# DATABASE_URL = "sqlite:///database.db"
DATABASE_URL = os.getenv("AZURE_POSTGRESQL_CONNECTION_STRING")
engine = create_engine(DATABASE_URL, echo=True)


class NotFoundError(Exception):
    pass


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
