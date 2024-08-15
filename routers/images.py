from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from starlette.responses import JSONResponse

from images.crud import delete_blob, generate_blob_name, list_blobs, upload_blob

router = APIRouter(prefix="/images")


# Upload pet image
@router.post("/")
async def upload_image(file: UploadFile = File(...), name: str = Query(None)):
    try:
        # Generate a unique blob name
        blob_name = generate_blob_name(file.filename, name)

        # Upload the file to Azure Blob Storage
        blob_url = upload_blob(file.file, blob_name)

        return JSONResponse(content={"url": blob_url, "image_name": blob_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List pet images
@router.get("/")
async def list_images():
    try:
        # List all blobs in the container
        blob_urls = list_blobs()
        return JSONResponse(content={"urls": blob_urls})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete pet image
@router.delete("/")
async def delete_image(name: str = Query(...)):
    try:
        # Replace spaces with underscores in the blob name
        blob_name = name.replace(" ", "_")

        # Delete the blob
        message = delete_blob(blob_name)

        return JSONResponse(content={"message": message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
