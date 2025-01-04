# from contextlib import asynccontextmanager

import uvicorn

# from database.core import init_db
from fastapi import FastAPI
from starlette.responses import JSONResponse

from app.database.models import Place, validate_schema_place
from app.routers.images import router as images_router
from app.routers.parks import router as parks_router
from app.routers.pets import router as pets_router
from app.routers.users import router as users_router

# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     init_db()
#     yield


app = FastAPI(
    title="Dogy Backend API",
    description="The Backend API for Dogy App",
    # lifespan=lifespan,
)

app.include_router(images_router, tags=["images"])
app.include_router(parks_router, tags=["parks"])
app.include_router(users_router, tags=["users"])
app.include_router(pets_router, tags=["pets"])
# app.include_router(notifications_router, tags=["notifications"])


# Entry
@app.get("/")
def api_entry():
    return JSONResponse(content={"message": "Welcome to the Dogy API!"})


@app.post("/validate_schema")
async def validate_schema_endpoint(park: Place | None = None):
    validate_schema_place(park)
    return JSONResponse(content={"result": "success"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
