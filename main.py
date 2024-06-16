from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from starlette.responses import JSONResponse
import uvicorn
from blobs import generate_blob_name, upload_blob, list_blobs, delete_blob
from parks import fetch_dog_parks_in_country

app = FastAPI()

@app.get("/")
async def api_entry():
    return {"message": "Dogy Backend API"}

@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...), name: str = Query(None)):
    try:
        # Generate a unique blob name
        blob_name = generate_blob_name(file.filename, name)

        # Upload the file to Azure Blob Storage
        blob_url = upload_blob(file.file, blob_name)

        return JSONResponse(content={"url": blob_url, "image_name": blob_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_images/")
async def list_images():
    try:
        # List all blobs in the container
        blob_urls = list_blobs()
        return JSONResponse(content={"urls": blob_urls})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_image/")
async def delete_image(name: str = Query(...)):
    try:
        # Replace spaces with underscores in the blob name
        blob_name = name.replace(" ", "_")

        # Delete the blob
        message = delete_blob(blob_name)

        return JSONResponse(content={"message": message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === PARKS ===
@app.get("/fetch_parks/")
async def fetch_parks(country: str = Query(...)):
    try:
        parks = fetch_dog_parks_in_country(country)
        if not parks:
            print("No parks found")  # Debug print

        return JSONResponse(content={"parks": parks, "total": len(parks)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
