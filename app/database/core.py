from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import DDL, SQLModel
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

PET_ATTR_VIEW = """
CREATE OR REPLACE VIEW pet_attr_view AS
SELECT
    attr.pet_id,
    attr.sterilized,
    COALESCE(breeds.breeds, '{}') AS breeds,
    COALESCE(aggression_levels.aggression_levels, '{}') AS aggression_levels,
    COALESCE(allergies.allergies, '{}') AS allergies,
    COALESCE(behaviors.behaviors, '{}') AS behaviors,
    COALESCE(interactions.interactions, '{}') AS interactions,
    COALESCE(personalities.personalities, '{}') AS personalities,
    COALESCE(reactivities.reactivities, '{}') AS reactivities
FROM pet_attr attr
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(breed) AS breeds
    FROM pet_attr_breed
    WHERE pet_attr_id = attr.id
) breeds ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(aggression_level) AS aggression_levels
    FROM pet_attr_aggression_level
    WHERE pet_attr_id = attr.id
) aggression_levels ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(allergy) AS allergies
    FROM pet_attr_allergy
    WHERE pet_attr_id = attr.id
) allergies ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(behavior) AS behaviors
    FROM pet_attr_behavior
    WHERE pet_attr_id = attr.id
) behaviors ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(interaction) AS interactions
    FROM pet_attr_interaction
    WHERE pet_attr_id = attr.id
) interactions ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(personality) AS personalities
    FROM pet_attr_personality
    WHERE pet_attr_id = attr.id
) personalities ON true
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(reactivity) AS reactivities
    FROM pet_attr_reactivity
    WHERE pet_attr_id = attr.id
) reactivities ON true;
"""

def create_views(target, connection, **kwargs):
    connection.execute(DDL(PET_ATTR_VIEW))

async def init_db() -> None:
    async with async_engine.begin() as conn:
        event.listen(SQLModel.metadata, "after_create", create_views)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session
