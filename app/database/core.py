
from azure.identity import EnvironmentCredential
from sqlalchemy.engine import URL
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()


class NotFoundError(Exception):
    pass

def get_postgresql_connection_string() -> str:
    """
    Generate PostgreSQL Connection String based on Azure Managed Identity
    """
    credential = EnvironmentCredential()
    token = credential.get_token(settings.db_token_endpoint)

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=settings.postgresql_user,
        password=token.token,
        host=settings.postgresql_host,
        port=5432,
        database=settings.postgresql_db_name,
    )
    return str(url)

DATABASE_URL = get_postgresql_connection_string()
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
