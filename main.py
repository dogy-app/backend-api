from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.responses import JSONResponse

from database.core import init_db
from database.models import Place, validate_schema_place
from routers.assistants import router as assistants_router
from routers.audio import router as audio_router
from routers.images import router as images_router
from routers.notifications import router as notifications_router
from routers.parks import router as parks_router


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
app.include_router(audio_router, tags=["audio"])
app.include_router(notifications_router, tags=["notifications"])
app.include_router(assistants_router, tags=["assistant"])


# Entry
@app.get("/")
def api_entry():
    return JSONResponse(content={"message": "Welcome to the Dogy API!"})


@app.post("/validate_schema")
async def validate_schema_endpoint(park: Place | None = None):
    validate_schema_place(park)
    return JSONResponse(content={"result": "success"})


# @app.post("/search_dog_parks/")
# async def search_dog_parks_endpoint(
#     db: Session = Depends(get_session), park: Place = None
# ):
#     result = validate_schema_place(park)
#     return JSONResponse(content={"result": "success"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
