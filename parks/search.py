import os
from typing import Self

import googlemaps
import pygeohash as pgh
import requests
from database.parks import (
    create_parks,
    map_park_details,
    map_parks_to_json,
    search_parks_db,
)
from sqlmodel import Session
from utils.azure import upload_image_to_azure


class SearchParks:
    def __init__(self, api_key: str, location: str):
        self.location = location
        self.api_key = api_key
        self.places = []
        self.gmaps = googlemaps.Client(key=api_key)

    def geohash(self, longitude: float, latitude: float) -> str:
        """
        Encode latitude and longitude into a geohash
        :param latitude: The latitude of the location
        :param longitude: The longitude of the location
        """
        return pgh.encode(latitude, longitude)

    def get_geocode_place(self, location):
        """
        Get the latitude, longitude, city, and country of a location
        :param location: The location to get metadata for (eg. Stockholm, Sweden)
        """

        _geocode = self.gmaps.geocode(location)
        if not _geocode:
            print(f"Failed to geocode location: {location}")
            return None

        return _geocode[0]

    def get_location_metadata_geocode(self, place):
        """
        Get the latitude, longitude, city, and country of a location
        :param location: The location to get metadata for (eg. Stockholm, Sweden)
        """
        geocode_place = self.get_geocode_place(place)
        city = None
        country = None

        location = geocode_place["geometry"]["location"]
        # FIXME: Retrieving city has to be done in a better way
        for component in geocode_place["address_components"]:
            if "locality" in component["types"]:
                city = component["long_name"]
            if "country" in component["types"]:
                country = component["long_name"]
            if "postal_town" in component["types"]:
                city = component["long_name"]

        return {
            "latitude": location["lat"],
            "longitude": location["lng"],
            "city": city,
            "country": country,
        }

    def get_location_metadata(self, place):
        """
        Get the latitude, longitude, city, and country of a location
        :param location: The location to get metadata for (eg. Stockholm, Sweden)
        """
        city = None
        country = None

        location = place["location"]
        # FIXME: Retrieving city has to be done in a better way
        for component in place["addressComponents"]:
            if "locality" in component["types"]:
                city = component["longText"]
            if "country" in component["types"]:
                country = component["longText"]
            if "postal_town" in component["types"]:
                city = component["longText"]

        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "city": city,
            "country": country,
        }

    def get_photo_url(self, place_url) -> str | None:
        """
        Get the photo URL for a place
        :param place_url: The URL for the place (eg. places/{place_id}/photos/{photo_id})
        """
        url = f"https://places.googleapis.com/v1/{place_url}/media?maxWidthPx=400&skipHttpRedirect=true"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
            },
        )

        if response.status_code != 200:
            print(f"Failed to retrieve photo: {response.text}")
            return None

        photo = response.json()
        return photo["photoUri"]

    def search_new_parks(self, max_result: int, radius: int) -> Self:
        """
        Search for parks in a given location based on latitude and longitude.
        :param location: The location to search for parks
        :param radius: The radius (meters) within which to search for parks
        """
        location_metadata = self.get_location_metadata_geocode(self.location)
        print(f"Location Metadata Geocode: {location_metadata}")
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.addressComponents,places.location,places.formattedAddress,places.id,places.photos,places.formattedAddress,places.websiteUri",
        }

        gmaps_response = requests.post(
            "https://places.googleapis.com/v1/places:searchNearby",
            headers=headers,
            json={
                "includedTypes": ["dog_park"],
                "maxResultCount": max_result,
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": location_metadata["latitude"],
                            "longitude": location_metadata["longitude"],
                        },
                        "radius": radius,
                    },
                },
            },
        )

        if gmaps_response.status_code != 200:
            print(f"Failed to retrieve parks: {gmaps_response.text}")
            raise NotImplementedError

        if "places" not in gmaps_response.json():
            print("No places found")
            self.places = []
            return self

        results = gmaps_response.json()
        self.places = results["places"]
        return self

    def _extract_park_details(self, place):
        """
        Extract park details from the search results
        :param place: The place to extract details from
        """
        location_metadata = self.get_location_metadata(place)
        return {
            "gmaps_id": place["id"],
            "name": place["displayName"]["text"],
            "city": location_metadata["city"],
            "country": location_metadata["country"],
            "geohash": self.geohash(
                longitude=location_metadata["longitude"],
                latitude=location_metadata["latitude"],
            ),
            "address": place["formattedAddress"],
            "geom": f"POINT ({location_metadata['longitude']} {location_metadata['latitude']})",
            "website_url": place["websiteUri"],
            "images": [
                upload_image_to_azure(
                    self.get_photo_url(place["photos"][0]["name"]),
                    f'{place["id"]}-{place["displayName"]["text"]}',
                )
            ],
            "type": "dog_park",
        }

    def extract_park_details(self) -> list[dict]:
        """
        Extract park details from the search results
        """
        results = self.places
        if len(results) == 0:
            return []

        park_details = map(self._extract_park_details, results)

        return list(park_details)


def search_parks(
    session: Session, location: str, radius: int = 10000, max_result: int = 20
):
    """
    Search for parks near a location within a given radius
    :param location: The location to search around (eg. Stockholm, Sweden)
    :param radius: The radius around the location to search in
    """
    search_park = SearchParks(api_key=os.getenv("GOOGLE_API_KEY"), location=location)
    location_metadata = search_park.get_location_metadata_geocode(location)
    existing_parks = search_parks_db(
        session=session,
        latitude=location_metadata["latitude"],
        longitude=location_metadata["longitude"],
        radius=radius,
    )
    print(len(existing_parks))
    if len(existing_parks) < 3:
        print(f"Searching new places for {location}")
        search_park.search_new_parks(max_result=max_result, radius=radius)
        parks = search_park.extract_park_details()
        if len(parks) == 0:
            print("No parks were found nearby")
            return []
        print("Adding new parks to the database")
        create_parks(session=session, parks=map_park_details(parks))
        return parks
    else:
        print("There are existing places nearby this location.")
        return map_parks_to_json(existing_parks)
