import requests
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from io import BytesIO
import uuid
import mimetypes
from firebase_setup import db  # Import the Firestore client

load_dotenv()

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GEOCODE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
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
    except requests.exceptions.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        raise

    data = response.json()
    parks = []

    for element in data.get('elements', []):
        name = element['tags'].get('name', 'Unnamed Dog Park')
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')

        city = fetch_nearest_city(lat, lon)
        image_url = fetch_park_image_and_upload(name, city, country)

        park_data = {
            "name": name,
            "city": city,
            "image": image_url,
            "location": [lat, lon],
            "country": country,
            "visitedBy": []
        }
        upload_to_firestore(park_data)
        parks.append(park_data)

    print(f"Found {len(parks)} parks")  # Debug print
    return parks

def fetch_nearest_city(lat, lon):
    params = {
        "latlng": f"{lat},{lon}",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(GOOGLE_GEOCODE_API_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Geocode API: {e}")
        return "Unknown"

    data = response.json()

    for result in data.get('results', []):
        for component in result['address_components']:
            if "locality" in component['types']:
                return component['long_name']
            if "administrative_area_level_2" in component['types']:
                return component['long_name']
            if "administrative_area_level_1" in component['types']:
                return component['long_name']

    if data.get('results'):
        return data['results'][0]['formatted_address']

    return "Unknown"

def fetch_park_image_and_upload(name, city, country):
    search_query = f"{name} {city} {country}"
    url = GOOGLE_PLACES_API_URL
    params = {
        "input": search_query,
        "inputtype": "textquery",
        "fields": "photos",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Places API: {e}")
        return None

    data = response.json()
    if data.get("candidates"):
        photo_reference = data["candidates"][0].get("photos", [{}])[0].get("photo_reference")
        if photo_reference:
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
            return upload_image_to_azure(photo_url, name)

    return None

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
        print(f"Uploaded image to Azure: {blob_url}")  # Debug print
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

def upload_to_firestore(park_data):
    try:
        db.collection('new_parks').add(park_data)
        print(f"Uploaded park data to Firestore: {park_data['name']}")  # Debug print
    except Exception as e:
        print(f"Error uploading park data to Firestore: {e}")
