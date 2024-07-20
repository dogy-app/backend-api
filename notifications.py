import os
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import HTTPException
import ably

load_dotenv()

ABLY_API_KEY = os.getenv("ABLY_API_KEY")

ably_client = ably.AblyRest(ABLY_API_KEY)

class PushNotification(BaseModel):
    title: str
    body: str
    token: str

class PushRecipient(BaseModel):
    transportType: str
    deviceToken: str

class PushDetails(BaseModel):
    recipient: PushRecipient

class DeviceInfo(BaseModel):
    manufacturer: str
    model: str
    os_version: str
    app_version: str

class DeviceRegistration(BaseModel):
    id: str
    platform: str
    form_factor: str
    push: PushDetails
    device_info: DeviceInfo

def send_notification(notification: PushNotification):
    try:
        response = ably_client.push.admin.publish_device(notification.token, {
            'notification': {
                'title': notification.title,
                'body': notification.body
            }
        })
        return {"message": "Notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def register_device(device: DeviceRegistration):
    try:
        response = ably_client.push.admin.device_registrations.save(device.dict())
        return {"message": "Device registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
