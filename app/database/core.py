from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import get_settings

settings = get_settings()


class NotFoundError(Exception):
    pass

# def get_postgresql_connection_string() -> str:
#     """
#     Generate PostgreSQL Connection String based on Azure Managed Identity
#     """
#     credential = EnvironmentCredential()
#     token = credential.get_token(settings.db_token_endpoint)
#
#     url = URL.create(
#         drivername="postgresql+psycopg",
#         username=settings.postgresql_user,
#         password=token.token,
#         host=settings.postgresql_host,
#         port=5432,
#         database=settings.postgresql_db_name,
#     )
#     return str(url)
def get_postgresql_connection_string() -> str:
    return "postgresql+psycopg://postgres:password@localhost:5432/dogyprod"

DATABASE_URL: str = get_postgresql_connection_string()
async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session
