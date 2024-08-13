import os
from typing import Self

import googlemaps
import pygeohash as pgh
import requests
from database import Database
from helpers import upload_image_to_azure


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

    def search_new_parks(self, location, radius=10000) -> Self:
        """
        Search for parks in a given location based on latitude and longitude.
        :param location: The location to search for parks
        :param radius: The radius (meters) within which to search for parks
        """
        location_metadata = self.get_location_metadata_geocode(location)
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
                "maxResultCount": 1,
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
            return []

        if "places" not in gmaps_response.json():
            print("No places found")

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
            "location": [location_metadata["latitude"], location_metadata["longitude"]],
            "website_url": place["websiteUri"],
            "image": upload_image_to_azure(
                self.get_photo_url(place["photos"][0]["name"]),
                place["displayName"]["text"],
            ),
            "visitedBy": [],
        }

    def extract_park_details(self):
        """
        Extract park details from the search results
        """
        results = self.places
        park_details = map(self._extract_park_details, results)

        return list(park_details)

    def insert_parks(self, park_details, database):
        """
        Insert parks into the database
        :param database: The database to insert the parks into
        """
        database.connect_db().set_collection("places", "dog_parks")
        database.insert_many(park_details)
        database.create_geospatial_index("location")

    def search_existing_parks(self, location, database, radius=10000):
        """
        Search for existing parks in a given location based on latitude and longitude.
        :param location: The location to search for parks
        :param radius: The radius (meters) within which to search for parks
        """
        location_metadata = self.get_location_metadata_geocode(location)
        database.connect_db().set_collection("places", "dog_parks")
        results = database.collection.find(
            {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [
                                location_metadata["longitude"],
                                location_metadata["latitude"],
                            ],
                        },
                        "$maxDistance": radius,
                    }
                }
            }
        )

        return results


def search_parks(location: str, radius: int):
    """
    Search for parks near a location within a given radius
    :param location: The location to search around (eg. Stockholm, Sweden)
    :param radius: The radius around the location to search in
    """
    database = Database(os.getenv("AZURE_COSMOSDB_CONNECTION_STRING"))
    database.connect_db().set_collection("places", "dog_parks")
    search_query = SearchParks(api_key="API_KEY", location="Stockholm, Sweden")
    search_query.search_new_parks(location, radius)
    park_details = search_query.extract_park_details()
    search_query.insert_parks(park_details, database)
    return park_details
