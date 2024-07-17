import googlemaps
import os
from dotenv import load_dotenv
import time
from math import radians, cos, sin, asin, sqrt
import pygeohash as pgh
from firebase_setup import db
from helpers import upload_image_to_azure

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize the Google Maps client with your API key
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def get_bounding_box(api_key, location):
    gmaps = googlemaps.Client(key=api_key)
    print(f"Geocoding location: {location}")

    # Geocoding an address
    geocode_result = gmaps.geocode(location)

    if not geocode_result:
        print("Geocode result is empty.")
        return None

    # Get the bounding box
    geometry = geocode_result[0]['geometry']
    bounds = geometry['bounds']

    # Bounding box
    bounding_box = {
        'northeast': bounds['northeast'],
        'southwest': bounds['southwest']
    }

    print(f"Bounding box for {location}: {bounding_box}")
    return bounding_box

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of earth in meters
    return c * r

def create_grid(bounding_box, grid_size=5000):
    print(f"Creating grid with size: {grid_size} meters")

    ne = bounding_box['northeast']
    sw = bounding_box['southwest']

    lat_diff = ne['lat'] - sw['lat']
    lng_diff = ne['lng'] - sw['lng']

    lat_steps = int(haversine(sw['lng'], sw['lat'], sw['lng'], ne['lat']) / grid_size)
    lng_steps = int(haversine(sw['lng'], sw['lat'], ne['lng'], sw['lat']) / grid_size)

    lat_step_size = lat_diff / lat_steps
    lng_step_size = lng_diff / lng_steps

    grid_centers = []

    for i in range(lat_steps + 1):
        for j in range(lng_steps + 1):
            lat = sw['lat'] + (i * lat_step_size) + (lat_step_size / 2)
            lng = sw['lng'] + (j * lng_step_size) + (lng_step_size / 2)
            grid_centers.append((lat, lng))

    print(f"Created {len(grid_centers)} grid centers")
    return grid_centers

def get_photo_url(photo_reference, api_key, max_width=400):
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={api_key}"


def extract_parks(results, city, country):
    parks = []
    for place in results:
        name = place['name']
        address = place.get('formatted_address', 'N/A')
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        geohash = pgh.encode(lat, lng)

        azure_photo_url = None  # Initialize the variable to avoid referencing it before assignment

        # Check if the park already exists in the database
        existing_park = db.collection('new_parks').where('geohash', '==', geohash).get()
        if existing_park:
            for doc in existing_park:
                park_data = doc.to_dict()
                if (park_data.get('name') == name and
                    park_data.get('address') == address and
                    park_data.get('image')):
                    azure_photo_url = park_data.get('image')
                    print(f"Park already exists: {park_data}")
                else:
                    # Update existing park details
                    if 'photos' in place:
                        photo_reference = place['photos'][0]['photo_reference']
                        photo_url = get_photo_url(photo_reference, GOOGLE_API_KEY)
                        azure_photo_url = upload_image_to_azure(photo_url, name) if photo_url else None
                    db.collection('new_parks').document(doc.id).set({
                        'name': name,
                        'location': [lat, lng],
                        'geohash': geohash,
                        'city': city,
                        'country': country,
                        'address': address,
                        'image': azure_photo_url,
                        'visitedBy': park_data.get('visitedBy', [])
                    })
                    print(f"Park updated: {name}")
        else:
            # If the park does not exist, add it to the collection
            if 'photos' in place:
                photo_reference = place['photos'][0]['photo_reference']
                photo_url = get_photo_url(photo_reference, GOOGLE_API_KEY)
                azure_photo_url = upload_image_to_azure(photo_url, name) if photo_url else None
            park = {
                'name': name,
                'location': [lat, lng],
                'geohash': geohash,
                'city': city,
                'country': country,
                'address': address,
                'image': azure_photo_url,
                'visitedBy': []
            }
            db.collection('new_parks').add(park)
            print(f"New park added: {name}")

        parks.append({
            'name': name,
            'location': [lat, lng],
            'geohash': geohash,
            'city': city,
            'country': country,
            'address': address,
            'image': azure_photo_url,
            'visitedBy': []
        })
    return parks

def search_dog_parks(location, grid_size=5000, results_limit=None):
    bounding_box = get_bounding_box(GOOGLE_API_KEY, location)

    if not bounding_box:
        print("Location not found or unable to retrieve bounding box.")
        return []

    grid_centers = create_grid(bounding_box, grid_size)

    all_parks = []
    seen_parks = set()

    city, country = location.split(", ")
    parks_count = 0

    # Perform a search within each grid
    for index, center in enumerate(grid_centers):
        if results_limit and parks_count >= results_limit:
            break
        print(f"Searching grid {index + 1}/{len(grid_centers)} at location {center}")
        places_result = gmaps.places(query="dog park", location=center, radius=grid_size)
        parks = extract_parks(places_result['results'], city, country)
        for park in parks:
            if results_limit and parks_count >= results_limit:
                break
            park_identifier = park['geohash']
            if park_identifier not in seen_parks:
                seen_parks.add(park_identifier)
                all_parks.append(park)
                parks_count += 1

        while 'next_page_token' in places_result:
            if results_limit and parks_count >= results_limit:
                break
            print("Fetching next page of results")
            # Wait for a short period before making the next request
            time.sleep(2)
            places_result = gmaps.places(query="dog park", location=center, page_token=places_result['next_page_token'])
            parks = extract_parks(places_result['results'], city, country)
            for park in parks:
                if results_limit and parks_count >= results_limit:
                    break
                park_identifier = park['geohash']
                if park_identifier not in seen_parks:
                    seen_parks.add(park_identifier)
                    all_parks.append(park)
                    parks_count += 1

    print(f"Number of unique results: {len(seen_parks)}")
    return all_parks
