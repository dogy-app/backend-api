import os
from dotenv import load_dotenv
import requests

load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

def register_device(device_token: str, device_type: int):
    url = "https://onesignal.com/api/v1/players"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "device_type": device_type,  # 1 for iOS, 2 for Android
        "identifier": device_token
    }

    response = requests.post(url, headers=headers, json=payload)
    return response

def subscribe_to_channel(device_token: str, channel_tag: str):
    url = f"https://onesignal.com/api/v1/players/{device_token}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "tags": {channel_tag: "subscribed"}
    }

    response = requests.put(url, headers=headers, json=payload)
    return response

def unsubscribe_from_channel(device_token: str, channel_tag: str):
    url = f"https://onesignal.com/api/v1/players/{device_token}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "tags": {channel_tag: ""}
    }

    response = requests.put(url, headers=headers, json=payload)
    return response

def send_notification(message: str, channel_tag: str = None):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "contents": {"en": message}
    }
    if channel_tag:
        payload["filters"] = [{"field": "tag", "key": channel_tag, "relation": "=", "value": "subscribed"}]

    response = requests.post(url, headers=headers, json=payload)
    return response
