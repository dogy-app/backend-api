from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

from parks.core import Park
from parks.search import search_parks

router = APIRouter(prefix="/parks")


class SearchParkQuery(BaseModel):
    location: str
    radius: int


@router.post("/search", response_model=Park)
async def search_park(search_query: SearchParkQuery):
    """
    Search for parks near a location within a given radius
    :param location: The location to search around (eg. Stockholm, Sweden)
    :param radius: The radius around the location to search in
    """
    try:
        # Call the search function from the core module
        parks = search_parks(search_query.location, search_query.radius)
        return JSONResponse(content={"parks": parks})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching parks: {e}")
