import requests
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from io import BytesIO
import uuid
import mimetypes
from firebase_setup import db
import pygeohash as pgh

load_dotenv()

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GEOCODE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
GOOGLE_PLACE_DETAILS_API_URL = "https://maps.googleapis.com/maps/api/place/details/json"
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_PARK_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def fetch_dog_parks_in_country(country):
    query = f"""
    [out:json][timeout:1800];
    area["name"="{country}"]["boundary"="administrative"]["admin_level"="2"]->.searchArea;
    (
      node["leisure"="dog_park"](area.searchArea);
      way["leisure"="dog_park"](area.searchArea);
      relation["leisure"="dog_park"](area.searchArea);
    );
    out center;
    """

    try:
        response = requests.post(OVERPASS_API_URL, data={'data': query})
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        return [], 0, 0

    if not data or 'elements' not in data or len(data['elements']) == 0:
        print("No elements found in Overpass API response")
        return [], 0, 0

    parks = []
    total_found = len(data['elements'])
    total_uploaded = 0

    for element in data.get('elements', []):
        osm_name = element['tags'].get('name', None)
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')

        google_name = fetch_park_name_from_google(lat, lon)
        places_name = fetch_park_name_from_places(lat, lon)

        name = select_valid_name(osm_name, google_name, places_name)
        geohash = pgh.encode(lat, lon)

        park_data = {
            "name": name,
            "city": None,
            "image": "",
            "location": [lat, lon],
            "country": country,
            "visitedBy": [],
            "geohash": geohash
        }

        image_url = fetch_park_image_and_upload(lat, lon, name, country)
        if image_url:
            park_data["image"] = image_url

        if is_duplicate_park(lat, lon):
            update_park_in_firestore(lat, lon, park_data)
        else:
            upload_to_firestore(park_data)
            parks.append(park_data)
            total_uploaded += 1

    print(f"Found {total_found} parks in {country}, uploaded {total_uploaded} to Firestore")
    return parks, total_found, total_uploaded

def select_valid_name(*names):
    for name in names:
        if name and name.lower() not in ["unnamed", "unknown", ""]:
            return name
    return "Dog Park"

def fetch_park_name_from_google(lat, lon):
    params = {
        "latlng": f"{lat},{lon}",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(GOOGLE_GEOCODE_API_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Geocode API: {e}")
        return None

    data = response.json()
    if 'results' not in data:
        print("No results found in Google Geocode API response")
        return None

    for result in data.get('results', []):
        for component in result['address_components']:
            if "park" in component['types']:
                return component['long_name']

    return None

def fetch_park_name_from_places(lat, lon):
    params = {
        "locationbias": f"point:{lat},{lon}",
        "input": "dog park",
        "inputtype": "textquery",
        "fields": "name",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(GOOGLE_PLACES_API_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Places API: {e}")
        return None

    data = response.json()
    if not data.get("candidates"):
        print("No candidates found in Google Places API response")
        return None

    return data["candidates"][0].get("name")

def fetch_park_image_and_upload(lat, lon, name, country):
    place_id = fetch_place_id(lat, lon, name, country)
    if place_id:
        photo_reference = fetch_photo_reference_from_place_id(place_id)
        if photo_reference:
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
            return upload_image_to_azure(photo_url, name)
    return None

def fetch_place_id(lat, lon, name, country):
    search_query = f"{name} {country}"
    url = GOOGLE_PLACES_API_URL
    params = {
        "input": search_query,
        "inputtype": "textquery",
        "fields": "place_id",
        "locationbias": f"point:{lat},{lon}",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Places API for place ID: {e}")
        return None

    data = response.json()
    if not data.get("candidates"):
        print("No candidates found in Google Places API response")
        return None

    return data["candidates"][0].get("place_id")

def fetch_photo_reference_from_place_id(place_id):
    url = GOOGLE_PLACE_DETAILS_API_URL
    params = {
        "place_id": place_id,
        "fields": "photos",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Places Details API: {e}")
        return None

    data = response.json()
    if "result" not in data or "photos" not in data["result"]:
        print("No photos found in Google Places Details API response")
        return None

    return data["result"]["photos"][0].get("photo_reference")

def upload_image_to_azure(photo_url, name):
    try:
        response = requests.get(photo_url)
        response.raise_for_status()
        image_data = BytesIO(response.content)

        content_type = response.headers.get('Content-Type')
        file_extension = mimetypes.guess_extension(content_type)

        if not file_extension:
            print(f"Unknown file extension for content type {content_type}")
            file_extension = '.jpg'

        blob_name = generate_blob_name(name, file_extension)
        blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=blob_name)
        blob_client.upload_blob(image_data, overwrite=True)
        blob_url = blob_client.url
        print(f"Uploaded image to Azure: {blob_url}")
        return blob_url
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
    except Exception as e:
        print(f"Error uploading image to Azure: {e}")
        return None

def generate_blob_name(name, extension):
    unique_id = uuid.uuid4()
    sanitized_name = name.replace(' ', '_').lower()
    return f"{sanitized_name}_{unique_id}{extension}"

def is_duplicate_park(lat, lon):
    try:
        docs = db.collection('new_parks').where('location', '==', [lat, lon]).get()
        print(f"Duplicate check for coordinates: {lat}, {lon} - {len(docs)} duplicates found")
        return len(docs) > 0
    except Exception as e:
        print(f"Error checking for duplicate parks: {e}")
        return False

def update_park_in_firestore(lat, lon, park_data):
    try:
        docs = db.collection('new_parks').where('location', '==', [lat, lon]).get()
        for doc in docs:
            # Update only the fields that have new data
            update_data = {
                "name": park_data["name"],
                "image": park_data["image"]
            }
            db.collection('new_parks').document(doc.id).update(update_data)
            print(f"Updated park data in Firestore: {park_data['name']}")
    except Exception as e:
        print(f"Error updating park data in Firestore: {e}")

def upload_to_firestore(park_data):
    try:
        db.collection('new_parks').add(park_data)
        print(f"Uploaded park data to Firestore: {park_data['name']}")
    except Exception as e:
        print(f"Error uploading park data to Firestore: {e}")
