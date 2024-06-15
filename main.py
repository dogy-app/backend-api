import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from starlette.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

# Azure storage connection string and container name
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

app = FastAPI()

@app.get("/")
async def api_entry():
    return {"message": "Dogy Backend API"}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), name: str = Query(None)):
    try:
        # Extract the file extension
        file_extension = os.path.splitext(file.filename)[1]

        # Create a unique name for the blob, replacing spaces with underscores
        base_name = name.replace(" ", "_") if name else file.filename.replace(" ", "_")

        # Generate a unique identifier
        unique_id = str(uuid.uuid4())

        # Construct the blob name with the unique identifier
        blob_name = f"{base_name}_{unique_id}{file_extension}"

        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)

        # Upload the file to Azure Blob Storage, overwriting if it exists
        blob_client.upload_blob(file.file, overwrite=True)

        # Get the URL of the uploaded file
        blob_url = blob_client.url

        return JSONResponse(content={"url": blob_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list/")
async def list_images():
    try:
        # Get the container client
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

        # List all blobs in the container
        blobs = container_client.list_blobs()

        # Get the URLs of the blobs
        blob_urls = [container_client.get_blob_client(blob).url for blob in blobs]

        return JSONResponse(content={"urls": blob_urls})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/")
async def delete_image(name: str = Query(...)):
    try:
        # Create a unique name for the blob, replacing spaces with underscores
        blob_name = name.replace(" ", "_")
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)

        # Delete the blob
        blob_client.delete_blob()

        return JSONResponse(content={"message": f"Blob '{blob_name}' deleted successfully."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
