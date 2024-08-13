from dotenv import load_dotenv
from pydantic import BaseModel

import os
from typing import List, Optional

from database import Database
from .search import SearchParks

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class Park(BaseModel):
    name: str
    country: str
    address: str
    city: str
    location: List[float]
    image: Optional[str] = None

if __name__ == "__main__":
    location = "Stockholm, Sweden"
    search_parks = SearchParks(GOOGLE_API_KEY, location)
    search_results = search_parks.search_new_parks(location).extract_park_details()
    # search_results = search_parks.search_existing_parks(location, Database(os.getenv("AZURE_COSMOSDB_CONNECTION_STRING")), radius=10000)
    search_parks.insert_parks(search_results, Database(os.getenv("AZURE_COSMOSDB_CONNECTION_STRING")))
    print(f"Search results: {search_results}")
