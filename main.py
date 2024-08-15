from contextlib import asynccontextmanager
from decimal import Decimal

import uvicorn
from fastapi import Depends, FastAPI
from sqlmodel import Session
from starlette.responses import JSONResponse

from database.core import get_session, init_db
from database.models import Park
from database.parks import create_parks
from routers.assistants import router as assistants_router
from routers.audio import router as audio_router
from routers.images import router as images_router
from routers.notifications import router as notifications_router
from routers.parks import router as parks_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Dogy Backend API",
    description="The Backend API for Dogy App",
    lifespan=lifespan,
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


@app.post("/search_dog_parks/")
async def search_dog_parks_endpoint(db: Session = Depends(get_session)):
    park = Park(
        name="Test Park",
        gmaps_id="test_id",
        city="Stockholm",
        country="Sweden",
        geohash="ashahstd",
        address="Test Address",
        image="https://testimage.com",
        latitude=Decimal(57.1124),
        longitude=Decimal(2.01654),
        website_url="https://testwebsite.com",
        visited_by=[],
    )

    result = create_parks(parks=[park], session=db)
    print(result)
    return JSONResponse(content={"result": "success"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
