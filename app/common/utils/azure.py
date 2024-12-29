import mimetypes
from io import BytesIO

import requests
from azure.identity import EnvironmentCredential
from azure.storage.blob import BlobServiceClient

from app.config import get_settings

credential = EnvironmentCredential()
settings = get_settings()


# Initialize the Azure Blob service client
blob_service_client = BlobServiceClient(account_url=settings.storage_account_url, credential=credential)

def upload_image_to_azure(photo_url, name):
    try:
        response = requests.get(photo_url)
        response.raise_for_status()
        image_data = BytesIO(response.content)

        content_type = response.headers.get("Content-Type")
        if not content_type:
            print(f"Unknown content type for image: {photo_url}")
            content_type = "image/jpeg"

        file_extension = mimetypes.guess_extension(content_type)

        if not file_extension:
            print(f"Unknown file extension for content type {content_type}")
            file_extension = ".jpg"

        blob_name = f"{name.replace(' ', '_')}{file_extension}"
        blob_client = blob_service_client.get_blob_client(
            container=settings.storage_pet_container_name, blob=blob_name
        )
        try:
            blob_client.get_blob_properties()
            blob_url = blob_client.url
            print(f"Image was already uploaded: {blob_url}")
        except:
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


def is_image_already_uploaded(blob_name):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=settings.storage_pet_container_name, blob=blob_name
        )
        return blob_client.exists()
    except Exception as e:
        print(f"Error checking if image exists: {e}")
        return False


def get_blob_url(blob_name):
    return f"{settings.storage_account_url}/{settings.storage_pet_container_name}/{blob_name}"
