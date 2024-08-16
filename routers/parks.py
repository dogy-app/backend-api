from database.core import get_session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from starlette.responses import JSONResponse

from parks.core import Park
from parks.search import search_parks

router = APIRouter(prefix="/parks")


class SearchParkQuery(BaseModel):
    location: str = "Stockholm, Sweden"
    max_result: int = 20
    radius: int = 10000


@router.post("/search", response_model=list[Park])
async def search_park(
    search_query: SearchParkQuery,
    db: Session = Depends(get_session),
):
    """
    Search for parks near a location within a given radius

    Args:
        search_query (`SearchParkQuery`): The search query
        db (`Session`): The database session

    Returns:
        parks (list[`Park`]): The list of parks near the location.

    Raises:
        `HTTPException`: Raises HTTP 500 if any error happened
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
