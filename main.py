from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from starlette.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
import pygeohash as pgh
from ask_dogy import ask_dogy, retrieve_assistant
from firebase_setup import db
from blobs import generate_blob_name, upload_blob, list_blobs, delete_blob
from search_parks import search_dog_parks
from speech_to_text import get_transcription
from parks import fetch_parks, add_new_park, edit_park_by_geohash, delete_park_by_geohash
from openai import AsyncOpenAI
from openai.types.beta import Thread, Assistant
import notifications
import os

app = FastAPI()

# Entry
@app.get("/")
async def api_entry():
    return {"message": "Dogy Backend API"}

# Upload pet image
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

# List pet images
@app.get("/list_images/")
async def list_images():
    try:
        # List all blobs in the container
        blob_urls = list_blobs()
        return JSONResponse(content={"urls": blob_urls})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete pet image
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
class Park(BaseModel):
    name: str
    country: str
    address: str
    city: str
    location: List[float]
    image: Optional[str] = None

@app.get("/parks/fetch/")
async def fetch_parks_endpoint():
    try:
        parks = fetch_parks()
        parks_data = [park.to_dict() for park in parks]
        return JSONResponse(content={"parks": parks_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parks/add/")
async def add_park_endpoint(park: Park):
    try:
        park_data = park.dict()
        add_new_park(park_data)
        return JSONResponse(content={"message": "Park added successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/parks/edit/{geohash}")
async def edit_park_endpoint(geohash: str, park: Park):
    try:
        park_data = park.dict()
        edit_park_by_geohash(geohash, park_data)
        return JSONResponse(content={"message": "Park updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/parks/delete/{geohash}")
async def delete_park_endpoint(geohash: str):
    try:
        delete_park_by_geohash(geohash)
        return JSONResponse(content={"message": "Park deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Search dog parks on Google Maps
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
    """
    Upload an audio file and get its transcription

    :param file: Audio file to transcribe
    :type file: UploadFile
    :return: Transcription of the audio file
    """

    try:
        # Get the filepath of the audio file and get its transcription
        transcription = get_transcription(file.filename)

        return JSONResponse(content={"response": transcription.text}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# === NOTIFICATIONS ===
class DeviceRegistration(BaseModel):
    user_id: str
    oneSignalPushId: str

class ChannelSubscription(BaseModel):
    device_token: str
    channel_tag: str

class NotificationMessage(BaseModel):
    title: str
    message: str
    channel_tag: str = None

class UserNotification(BaseModel):
    title: str
    message: str
    user_id: str
    subtitle: str = None

class NotificationSchedule(BaseModel):
    user_id: str
    hour: int
    minute: int
    title: str
    message: str
    pet_name: str
    subtitle: str = None
class CancelNotification(BaseModel):
    notification_id: str

# Register a device
@app.post("/notifications/register_device/")
async def register_device(device_registration: DeviceRegistration):
    response = notifications.register_device(device_registration.user_id, device_registration.oneSignalPushId)
    if 'error' in response:
        raise HTTPException(status_code=500, detail=response['error'])
    return response

# Subscribe to a channel
@app.post("/notifications/subscribe_to_channel/")
async def subscribe_to_channel(subscription: ChannelSubscription):
    response = notifications.subscribe_to_channel(subscription.device_token, subscription.channel_tag)

    if response.status_code == 200:
        return {"message": "Subscribed to channel successfully", "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Unsubscribe from a channel
@app.post("/notifications/unsubscribe_from_channel/")
async def unsubscribe_from_channel(subscription: ChannelSubscription):
    response = notifications.unsubscribe_from_channel(subscription.device_token, subscription.channel_tag)

    if response.status_code == 200:
        return {"message": "Unsubscribed from channel successfully", "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Send a notification to a channel
@app.post("/notifications/send_notification_to_channel/")
async def send_notification(notification: NotificationMessage):
    response = notifications.send_notification_to_channel(notification.title, notification.message, notification.channel_tag)

    if response.status_code == 200:
        return {"message": "Notification sent successfully", "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

# Send a notification to a specific user
@app.post("/notifications/send_notification_to_user/")
async def send_notification_to_user(user_notification: UserNotification):
    response = notifications.send_notification_to_user(
        user_notification.title,
        user_notification.message,
        user_notification.user_id,
        user_notification.subtitle
    )

    if 'error' in response:
        raise HTTPException(status_code=500, detail=response['error'])
    return {"message": "Notification sent to user successfully", "response": response}

# Schedule a daily notification
@app.post("/notifications/create_daily_notification/")
async def schedule_daily_notification(schedule: NotificationSchedule):
    response = notifications.store_daily_notification(
        schedule.user_id, schedule.hour, schedule.minute, schedule.title, schedule.message, schedule.pet_name, schedule.subtitle
    )

    # Ensure response is a dictionary and check for 'error' key
    if isinstance(response, dict) and 'error' in response:
        raise HTTPException(status_code=500, detail=response['error'])

    # If response is not a dictionary, raise a different error
    if not isinstance(response, dict):
        raise HTTPException(status_code=500, detail="Invalid response from notification storage method.")

    return {"message": "Notification scheduled successfully", "response": response}

# Cancel a daily notification
@app.post("/notifications/cancel_scheduled_notification/")
async def cancel_notification(cancel: CancelNotification):
    response = notifications.cancel_scheduled_notification(cancel.notification_id)
    if 'error' in response:
        raise HTTPException(status_code=500, detail=response['error'])

    return response

# === ASK DOGY ===
class UserMessage(BaseModel):
    user_message: str
    user_name: str
    assistant_id: Optional[str] = None
    thread_id: Optional[str] = None

# Create a thread first before asking Dogy (run only once)
@app.get("/create-thread/")
async def create_thread():
    """
    Create a thread to interact with Dogy.

    :return: Thread ID
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    thread: Thread = await client.beta.threads.create()
    return {"thread_id": thread.id}

@app.post("/ask-dogy/")
async def dogy_assistant(user_message: UserMessage):
    """
    Ask Dogy a question. Use the same assistant ID and thread ID for the same
    conversation.

    :param user_message: User message and user name. Optionally, you can provide
    the assistant ID and thread ID to continue the conversation.
    :return: Dogy's response, assistant ID, and thread ID.
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    assistant_id = await retrieve_assistant(user_message.user_message)
    print(assistant_id)
    user_message.assistant_id = assistant_id

    if not assistant_id:
        raise HTTPException(status_code=500, detail="Assistant ID failed to retrieve")

    await client.beta.assistants.retrieve(assistant_id=assistant_id)
    if not user_message.thread_id:
        ids = await create_thread()
        user_message.thread_id = ids['thread_id']

    print(f"Assistant ID: {user_message.assistant_id}")
    print(f"Thread ID: {user_message.thread_id}")
    response = await ask_dogy(
        user_message.user_message,
        user_message.user_name,
        user_message.assistant_id,
        user_message.thread_id
    )

    return {
        "response": response,
        "assistant_id": user_message.assistant_id,
        "thread_id": user_message.thread_id
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
