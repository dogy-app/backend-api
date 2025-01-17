from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from starlette.responses import JSONResponse

from .config import get_settings
from .database.core import async_engine, init_db
from .errors import register_all_errors
from .routers.images import router as images_router
from .routers.pets import router as pets_router
from .routers.users import router as users_router

settings = get_settings()
version_prefix = f"/api/{settings.api_version}"

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
    root_path=version_prefix,
    version="0.1.0"
)

register_all_errors(app)

app.openapi_tags = [
    {"name": "Entry", "description": "API Entry"},
    {"name": "Images", "description": "Image Handling for App Uploads"},
    {"name": "Users", "description": "Users Management"},
    {"name": "Pets", "description": "Manage Pets that are associated with users."},
]

app.include_router(images_router, prefix="/images", tags=["Images"])
# app.include_router(parks_router, tags=["parks"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(pets_router, prefix="/pets", tags=["Pets"])
# app.include_router(notifications_router, tags=["notifications"])


# Entry
@app.get("/", tags=["Entry"])
def api_entry():
    return JSONResponse(content={"message": "Welcome to the Dogy API!"})

@app.get("/scalar", tags=["Entry"])
async def scalar_html():
    return get_scalar_api_reference(
        title=app.title,
        openapi_url=app.openapi_url,
        scalar_theme="saturn"
    )
