from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import JSONResponse

from .database.core import async_engine, init_db
from .routers.images import router as images_router
from .routers.pets import router as pets_router
from .routers.users import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup Sequence
    await init_db()
    yield
    # Shutdown Sequence
    await async_engine.dispose()


app = FastAPI(
    title="Dogy Backend API",
    description="The Backend API for Dogy App",
    lifespan=lifespan,
    prefix="/api/v1"
)

app.include_router(images_router, tags=["images"])
# app.include_router(parks_router, tags=["parks"])
app.include_router(users_router, tags=["users"])
app.include_router(pets_router, tags=["pets"])
# app.include_router(notifications_router, tags=["notifications"])


# Entry
@app.get("/")
def api_entry():
    return JSONResponse(content={"message": "Welcome to the Dogy API!"})
