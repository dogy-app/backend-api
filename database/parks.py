from shapely import wkb
from sqlalchemy import text
from sqlmodel import Session
from binascii import unhexlify

from .models import Place


def map_park_details(park_details: list[dict]) -> list[Place]:
    return [Place(**park) for park in park_details]


def wkb_to_coords(wkb_element: str):
    wkb_bytes = unhexlify(wkb_element)
    point = wkb.loads(wkb_bytes)
    return point.x, point.y


def search_parks_db(
    *, session: Session, latitude: float, longitude: float, radius: int, limit: int
):
    # point = WKTElement(f"POINT({longitude:.4f} {latitude:.4f})", srid=4326)
    # query = select(
    #     Place.geom,
    #     Place.name,
    #     Place.description,
    #     Place.gmaps_id,
    #     Place.city,
    #     Place.country,
    #     Place.geohash,
    #     Place.address,
    #     Place.images,
    #     Place.website_url,
    # ).where((Place.type == "dog_park") & func.ST_DWithin(Place.geom, point, radius))
    raw_sql = text("""
    SELECT geom, name, description, gmaps_id, city, country, geohash, address, images, website_url
    FROM places
    WHERE type = 'dog_park'
    AND ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography, :radius)
    LIMIT :limit;
    """)

    results = session.execute(
        raw_sql,
        {
            "longitude": round(longitude, 4),
            "latitude": round(latitude, 4),
            "radius": radius,
            "limit": limit,
        },
    ).fetchall()

    if not results:
        print("No places found in this location.")
        return []

    return results


def map_parks_to_json(results):
    mapped_result = []
    for item in results:
        (
            wkb_element,
            name,
            description,
            gmaps_id,
            city,
            country,
            geohash,
            address,
            images,
            website_url,
        ) = item

        # Convert WKBElement to POINT
        longitude, latitude = wkb_to_coords(wkb_element)

        # Create the dictionary
        record = {
            "gmaps_id": gmaps_id,
            "name": name,
            "city": city,
            "country": country,
            "geohash": geohash,
            "address": address,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "website_url": website_url,
            "images": images,
        }

        mapped_result.append(record)

    return mapped_result


def create_parks(*, session: Session, parks: list[Place]):
    session.add_all(parks)
    session.commit()
    print("Parks added successfully")
    return parks
