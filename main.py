from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from starlette.responses import JSONResponse
from blobs import generate_blob_name, upload_blob, list_blobs, delete_blob
from firebase_setup import db
from search_parks import search_dog_parks
from speech_to_text import get_transcription
import uvicorn
import pygeohash as pgh

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
async def update_geohashes():
    try:
        parks_ref = db.collection('new_parks')
        parks = parks_ref.stream()

        for park in parks:
            park_data = park.to_dict()
            location = park_data.get("location")
            if location:
                lat, lon = location
                geohash = pgh.encode(lat, lon)
                parks_ref.document(park.id).update({"geohash": geohash})

        return {"message": "Geohashes updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_dog_parks/")
async def search_dog_parks_endpoint(location: str = Query(...), grid_size: int = Query(5000), results_limit: int = Query(None)):
    try:
        results = search_dog_parks(location, grid_size, results_limit)
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Speech-to-text
@app.post("/audio/transcriptions/create")
async def upload_audio(file: UploadFile = File(...)):
    try:
        transcription = get_transcription(file.filename)

        return JSONResponse(content={"response": transcription.text}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
