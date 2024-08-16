import mimetypes
import os
from io import BytesIO

import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_PARK_CONTAINER_NAME")

# Initialize the Azure Blob service client
blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)


def upload_image_to_azure(photo_url, name):
    try:
        response = requests.get(photo_url)
        response.raise_for_status()
        image_data = BytesIO(response.content)

        content_type = response.headers.get("Content-Type")
        file_extension = mimetypes.guess_extension(content_type)

        if not file_extension:
            print(f"Unknown file extension for content type {content_type}")
            file_extension = ".jpg"

        blob_name = f"{name.replace(' ', '_')}{file_extension}"
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_STORAGE_CONTAINER_NAME, blob=blob_name
        )
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
            container=AZURE_STORAGE_CONTAINER_NAME, blob=blob_name
        )
        return blob_client.exists()
    except Exception as e:
        print(f"Error checking if image exists: {e}")
        return False


def get_blob_url(blob_name):
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER_NAME}/{blob_name}"
