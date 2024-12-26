from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from app.images.crud import delete_blob, generate_blob_name, list_blobs, upload_blob

router = APIRouter(prefix="/images")


class UploadImageResponse(BaseModel):
    url: str = Field(
        ...,
        example="https://dogyappuploads.blob.core.windows.net/parkimages/ChIJQ7lde9p3X0YRGTgpY_sOEsI-Langholmen_Dog_Beach.jpg",
    )
    image_name: str = Field(..., example="Langholmen Dog Beach")


class ListImageResponse(BaseModel):
    urls: list[str] = Field(
        ...,
        example=[
            "https://dogyappuploads.blob.core.windows.net/parkimages/ChIJQ7lde9p3X0YRGTgpY_sOEsI-Langholmen_Dog_Beach.jpg"
        ],
    )


class DeleteImageResponse(BaseModel):
    message: str = Field(
        ..., example="Blob 'Langholmen Dog Beach' deleted successfully."
    )


# Upload pet image
@router.post("/", response_model=UploadImageResponse)
async def upload_image(file: UploadFile = File(...), name: str = Query(None)):
    """
    Upload an image

    Args:
        file (`UploadFile`): The file to be uploaded
        name (`str`): The name of the file when it is uploaded

    Returns:
        url (`str`): The blob url of the file
        image_name (`str`): The image name of the file

    Raises:
        `HTTPException`: Raises HTTP 500 if any error happened
    """
    try:
        # Generate a unique blob name
        blob_name = generate_blob_name(file.filename, name)

        # Upload the file to Azure Blob Storage
        blob_url = upload_blob(file.file, blob_name)

        return JSONResponse(content={"url": blob_url, "image_name": blob_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List pet images
@router.get("/", response_model=ListImageResponse)
async def list_images():
    """
    List all images

    Returns:
        urls (`str`)

    Raises:
        `HTTPException`: Raises HTTP 500 if any error happened
    """
    try:
        # List all blobs in the container
        blob_urls = list_blobs()
        return JSONResponse(content={"urls": blob_urls})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete pet image
@router.delete("/", response_model=DeleteImageResponse)
async def delete_image(name: str = Query(...)):
    """
    Delete an image

    Args:
        name (`str`): The name of the image to be deleted

    Returns:
        `JSONResponse`: Returns a message `message` indicating the deletion status

    Raises:
        `HTTPException`: Raises HTTP 500 if any error happened
    """
    try:
        # Replace spaces with underscores in the blob name
        blob_name = name.replace(" ", "_")

        # Delete the blob
        message = delete_blob(blob_name)

        return JSONResponse(content={"message": message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
