
from pydantic import BaseModel


class Park(BaseModel):
    gmaps_id: str 
    name: str 
    city: str 
    country: str 
    geohash: str 
    address: str 
    location: dict 
    images: list[str]     
    website_url: str 

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "gmaps_id": "ChIJQ7lde9p3X0YRGTgpY_sOEsI",
                "name": "Langholmen Dog Beach",
                "city": "Stockholm",
                "country": "Sweden",
                "geohash": "u6sc6rksr542",
                "address": "Långholmsbacken 9, 117 33 Stockholm, Sweden",
                "location": {
                    "latitude": 59.3206,
                    "longitude": 18.0329,
                    },
                "images": [
                    "https://dogyappuploads.blob.core.windows.net/parkimages/ChIJQ7lde9p3X0YRGTgpY_sOEsI-Langholmen_Dog_Beach.jpg",
                    ],
                "website_url": "https://parker.stockholm/hitta-badplats/badplats/langholmens-klippbad/",
                    }

                ]
        }
    }
