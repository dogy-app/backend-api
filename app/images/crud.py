import os
import uuid

from azure.identity import EnvironmentCredential
from azure.storage.blob import BlobServiceClient

from app.config import get_settings

settings = get_settings()
credential = EnvironmentCredential()

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient(account_url=settings.storage_account_url, credential=credential)


def generate_blob_name(file_name: str, custom_name: str | None = None) -> str:
    """
    Generate a unique blob name using the custom name or file name, and appending a unique identifier.
    """
    if (len(file_name) == 0):
        raise ValueError("File name cannot be empty.")

    # Extract the file extension
    file_extension = os.path.splitext(file_name)[1]
    file_name = os.path.splitext(file_name)[0]

    # Create a base name, replacing spaces with underscores
    base_name = (
        custom_name.replace(" ", "_") if custom_name else file_name.replace(" ", "_")
    )

    # Generate a unique identifier
    unique_id = str(uuid.uuid4())

    # Construct the blob name with the unique identifier
    blob_name = f"{base_name}_{unique_id}{file_extension}"

    return blob_name


def upload_blob(file, blob_name: str):
    """
    Upload a file to Azure Blob Storage with the given blob name.
    """
    blob_client = blob_service_client.get_blob_client(
        container=settings.storage_pet_container_name, blob=blob_name
    )
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url


def list_blobs():
    """
    List all blobs in the Azure Blob Storage container and return their URLs.
    """
    container_client = blob_service_client.get_container_client(settings.storage_pet_container_name)
    blobs = container_client.list_blobs()
    blob_urls = [container_client.get_blob_client(blob.name).url for blob in blobs]
    return blob_urls


def delete_blob(blob_name: str):
    """
    Delete a blob from Azure Blob Storage with the given blob name.
    """
    blob_client = blob_service_client.get_blob_client(
        container=settings.storage_pet_container_name, blob=blob_name
    )
    blob_client.delete_blob()
    return f"Blob '{blob_name}' deleted successfully."
