import os
import uuid

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure storage connection string and container name
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)


def generate_blob_name(file_name: str, custom_name: str = None) -> str:
    """
    Generate a unique blob name using the custom name or file name, and appending a unique identifier.
    """
    # Extract the file extension
    file_extension = os.path.splitext(file_name)[1]

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
        container=AZURE_CONTAINER_NAME, blob=blob_name
    )
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url


def list_blobs():
    """
    List all blobs in the Azure Blob Storage container and return their URLs.
    """
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
    blobs = container_client.list_blobs()
    blob_urls = [container_client.get_blob_client(blob).url for blob in blobs]
    return blob_urls


def delete_blob(blob_name: str):
    """
    Delete a blob from Azure Blob Storage with the given blob name.
    """
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME, blob=blob_name
    )
    blob_client.delete_blob()
    return f"Blob '{blob_name}' deleted successfully."
