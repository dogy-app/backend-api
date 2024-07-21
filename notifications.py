import os
from dotenv import load_dotenv
import requests

load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

def subscribe_to_channel(device_token: str, channel_tag: str):
    url = f"https://onesignal.com/api/v1/players/{device_token}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "tags": {channel_tag: "subscribed"}
    }

    response = requests.put(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Subscribe to Channel Response (raw):", response.text)
        response.raise_for_status()
    print("Subscribe to Channel Response:", response_data)
    return response

def unsubscribe_from_channel(device_token: str, channel_tag: str):
    url = f"https://onesignal.com/api/v1/players/{device_token}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "tags": {channel_tag: ""}
    }

    response = requests.put(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Unsubscribe from Channel Response (raw):", response.text)
        response.raise_for_status()
    print("Unsubscribe from Channel Response:", response_data)
    return response

def send_notification(title: str, message: str, channel_tag: str = None):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message}
    }
    if channel_tag:
        payload["filters"] = [{"field": "tag", "key": channel_tag, "relation": "=", "value": "subscribed"}]

    response = requests.post(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Send Notification Response (raw):", response.text)
        response.raise_for_status()
    print("Send Notification Response:", response_data)
    return response

def send_notification_to_user(title: str, message: str, user_id: str):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message},
        "include_player_ids": [user_id]
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Send Notification to User Response (raw):", response.text)
        response.raise_for_status()
    print("Send Notification to User Response:", response_data)
    return response
