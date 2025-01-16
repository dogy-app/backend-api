from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.images.crud import delete_blob, generate_blob_name, upload_blob

router = APIRouter()


class UploadImageResponse(BaseModel):
    url: str
    image_name: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://dogyappuploads.blob.core.windows.net/parkimages/ChIJQ7lde9p3X0YRGTgpY_sOEsI-Langholmen_Dog_Beach.jpg",
                "image_name": "Langholmen Dog Beach"
            }
        }
    }


class DeleteImageResponse(BaseModel):
    message: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Blob 'Langholmen Dog Beach' deleted successfully."
            }
        }
    }


# Upload pet image
@router.post("/", response_model=UploadImageResponse)
async def upload_image(
        file: UploadFile = File(...,
    description="File to be uploaded. Must be an image file and is in formData format."),
        name: str = Query(None)
):
    """
    Upload an image to Azure Blob Storage.
    The filename will be converted to snake case in the uploaded blob name.
    """
    try:
        # Generate a unique blob name
        blob_name = generate_blob_name(file.filename, name)

        # Upload the file to Azure Blob Storage
        blob_url = upload_blob(file.file, blob_name)

        return JSONResponse(content={"url": blob_url, "image_name": blob_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/", response_model=DeleteImageResponse)
async def delete_image(name: str = Query(...)):
    """
    Delete an image from Azure Blob Storage.
    """
    try:
        # Replace spaces with underscores in the blob name
        blob_name = name.replace(" ", "_")

        # Delete the blob
        message = delete_blob(blob_name)

        return JSONResponse(content={"message": message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
