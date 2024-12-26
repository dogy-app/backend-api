import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class Park(BaseModel):
    gmaps_id: str = Field(..., example="ChIJQ7lde9p3X0YRGTgpY_sOEsI")
    name: str = Field(..., example="Langholmen Dog Beach")
    city: str = Field(..., example="Stockholm")
    country: str = Field(..., example="Sweden")
    geohash: str = Field(..., example="u6sc6rksr542")
    address: str = Field(..., example="Långholmsbacken 9, 117 33 Stockholm, Sweden")
    location: dict = Field(
        ...,
        example={
            "latitude": 59.3206,
            "longitude": 18.0329,
        },
    )
    images: list[str] = Field(
        ...,
        example=[
            "https://dogyappuploads.blob.core.windows.net/parkimages/ChIJQ7lde9p3X0YRGTgpY_sOEsI-Langholmen_Dog_Beach.jpg",
        ],
    )
    website_url: str = Field(
        ...,
        example="https://parker.stockholm/hitta-badplats/badplats/langholmens-klippbad/",
    )
