from database.core import get_session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from starlette.responses import JSONResponse

from parks.core import Park
from parks.search import search_parks

router = APIRouter(prefix="/parks")


class SearchParkQuery(BaseModel):
    location: str
    max_result: int = 20
    radius: int = 10000


@router.post("/search", response_model=Park)
async def search_park(
    search_query: SearchParkQuery,
    db: Session = Depends(get_session),
):
    """
    Search for parks near a location within a given radius
    :param location: The location to search around (eg. Stockholm, Sweden)
    :param radius: The radius around the location to search in
    """
    try:
        search_results = search_parks(
            session=db,
            location=search_query.location,
            max_result=search_query.max_result,
            radius=search_query.radius,
        )
        print(search_results)
        return JSONResponse(content={"parks": search_results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching parks: {e}")
