import os

from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app

load_dotenv()

# Azure Storage settings
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_ESSENTIALS_CONTAINER_NAME")
AZURE_STORAGE_BLOB_NAME = os.getenv("AZURE_STORAGE_FIREBASE_KEY_BLOB_NAME")
LOCAL_FILE_PATH = "../firebase-service-account.json"


def download_file_from_azure():
    from azure.storage.blob import BlobServiceClient

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME, blob=AZURE_STORAGE_BLOB_NAME
    )

    with open(LOCAL_FILE_PATH, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())


# Download the service account key JSON file from Azure Storage
download_file_from_azure()

# Initialize Firebase with the downloaded service account key JSON file
cred = credentials.Certificate(LOCAL_FILE_PATH)
initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()
