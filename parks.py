import argparse
from firebase_setup import db
from helpers import upload_image_to_azure, is_image_already_uploaded, get_blob_url
import pygeohash as pgh

def fetch_parks(batch_size=20):
    parks_ref = db.collection('new_parks')
    parks = []
    next_page_token = None

    def fetch_page(token):
        query = parks_ref.limit(batch_size)
        if token:
            query = query.start_after(token)
        return query.stream()

    while True:
        page = fetch_page(next_page_token)
        page_parks = list(page)
        if not page_parks:
            break
        parks.extend(page_parks)
        next_page_token = page_parks[-1]

    return parks

def display_parks(parks):
    for park in parks:
        print(f"Park ID: {park.id}")
        print(f"Park Data: {park.to_dict()}")
        print("------")

def find_park_by_geohash(geohash):
    parks_ref = db.collection('new_parks')
    query = parks_ref.where('geohash', '==', geohash).stream()
    for park in query:
        return park
    return None

def add_new_park(new_park_data):
    try:
        lat, lng = map(float, new_park_data['location'])
        geohash = pgh.encode(lat, lng)
        existing_park = find_park_by_geohash(geohash)

        if existing_park:
            print("Park already exists. Please use the update method instead.")
            return

        # Upload image if provided and not already uploaded
        image_url = None
        if new_park_data.get('image'):
            image_name = f"{new_park_data['name'].replace(' ', '_')}.jpg"  # Assuming jpg, adjust as needed
            if not is_image_already_uploaded(image_name):
                image_url = upload_image_to_azure(new_park_data['image'], new_park_data['name'])
            else:
                image_url = get_blob_url(image_name)

        # Prepare park data for Firestore
        new_park = {
            'image': image_url,
            'country': new_park_data['country'],
            'address': new_park_data['address'],
            'geohash': geohash,
            'visitedBy': [],  # Initialize visitedBy as an empty list
            'city': new_park_data['city'],
            'location': [lat, lng],
            'name': new_park_data['name']
        }

        # Add new park to Firestore
        db.collection('new_parks').add(new_park)
        print(f"Added new park: {new_park}")

    except Exception as e:
        print(f"Error adding park: {e}")

def edit_park_by_geohash(geohash, updated_park_data):
    try:
        park = find_park_by_geohash(geohash)

        if not park:
            print(f"Park with geohash {geohash} does not exist.")
            return

        park_ref = db.collection('new_parks').document(park.id)
        update_data = {}
        existing_park_data = park.to_dict()

        # Check if each field is provided and different from the current value
        if 'country' in updated_park_data and updated_park_data['country'] != existing_park_data['country']:
            update_data['country'] = updated_park_data['country']

        if 'address' in updated_park_data and updated_park_data['address'] != existing_park_data['address']:
            update_data['address'] = updated_park_data['address']

        if 'city' in updated_park_data and updated_park_data['city'] != existing_park_data['city']:
            update_data['city'] = updated_park_data['city']

        if 'name' in updated_park_data and updated_park_data['name'] != existing_park_data['name']:
            update_data['name'] = updated_park_data['name']

        if 'location' in updated_park_data and updated_park_data['location'] != existing_park_data['location']:
            lat, lng = map(float, updated_park_data['location'])
            update_data['location'] = [lat, lng]
            update_data['geohash'] = pgh.encode(lat, lng)

        # Upload new image if provided and not already uploaded
        if 'image' in updated_park_data and updated_park_data['image']:
            image_name = f"{updated_park_data['name'].replace(' ', '_')}.jpg"  # Assuming jpg, adjust as needed
            if not is_image_already_uploaded(image_name):
                image_url = upload_image_to_azure(updated_park_data['image'], updated_park_data['name'])
            else:
                image_url = get_blob_url(image_name)
            update_data['image'] = image_url
        elif 'image' not in updated_park_data:
            # Keep the existing image if no new image is provided
            update_data['image'] = existing_park_data.get('image', None)

        # Update Firestore document if there is any new data to update
        if update_data:
            park_ref.update(update_data)
            print(f"Updated park with geohash: {geohash} with data: {update_data}")
        else:
            print("No new data to update.")

    except Exception as e:
        print(f"Error editing park: {e}")

def delete_park_by_geohash(geohash):
    try:
        park = find_park_by_geohash(geohash)

        if not park:
            print(f"Park with geohash {geohash} does not exist.")
            return

        park_ref = db.collection('new_parks').document(park.id)
        park_ref.delete()
        print(f"Deleted park with geohash: {geohash}")

    except Exception as e:
        print(f"Error deleting park: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Park management script.')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    subparsers.add_parser('fetch', help='Fetch and display parks')

    add_parser = subparsers.add_parser('add', help='Add a new park')

    edit_parser = subparsers.add_parser('edit', help='Edit a predefined park')
    edit_parser.add_argument('geohash', type=str, help='Geohash of the park to edit')

    delete_parser = subparsers.add_parser('delete', help='Delete a park')
    delete_parser.add_argument('geohash', type=str, help='Geohash of the park to delete')

    args = parser.parse_args()

    # New park data example
    new_park_data = {
        'image': 'https://lh5.googleusercontent.com/p/AF1QipPIzvD6bTFRH0P1mYU0kvMKc-KuHPeIOCPqtqOH=w408-h544-k-no',
        'country': 'Sweden',
        'address': 'Bräcke Östergårds väg, 418 77 Göteborg',
        'city': 'Gothenburg',
        'location': ['57.713103569491146', '11.897711153167405'],
        'name': 'Bräckeberget Rastgård'
    }

    # Updated park data example
    updated_park_data = {
        'image': '',
        'country': 'Sweden',
        'address': 'Bräcke Östergårds väg, 418 77 Göteborg',
        'city': 'Göteborg',
        'location': ['57.713103569491146', '11.897711153167405'],
        'name': 'Bräckeberget Rastgård'
    }

    if args.command == 'fetch':
        parks = fetch_parks()
        display_parks(parks)
    elif args.command == 'add':
        add_new_park(new_park_data)
    elif args.command == 'edit':
        edit_park_by_geohash(args.geohash, updated_park_data)
    elif args.command == 'delete':
        delete_park_by_geohash(args.geohash)
    else:
        parser.print_help()
