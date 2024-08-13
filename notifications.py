import os
import requests
from firebase_setup import db
from google.cloud.firestore import ArrayUnion
import logging
from dotenv import load_dotenv

load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Register a device for push notifications
def register_device(user_id: str, oneSignalPushId: str):
    try:
        # Register device in the database
        user_ref = db.collection("users").document(user_id)
        user_ref.update({"pushIDs": ArrayUnion([oneSignalPushId])})
        logger.info(f"Device registered successfully for user: {user_id}")
        return {"message": "Device registered successfully"}
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        return {"error": str(e)}


# Send a notification to a user
def send_notification_to_user(
    title: str, message: str, user_id: str, subtitle: str = None
):
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return {"error": "User not found"}

        user_data = user_doc.to_dict()
        oneSignalPushIds = user_data.get("pushIDs", [])

        if not oneSignalPushIds:
            return {"error": "No OneSignal Push IDs found for user"}

        url = "https://onesignal.com/api/v1/notifications"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {ONESIGNAL_API_KEY}",
        }
        payload = {
            "app_id": ONESIGNAL_APP_ID,
            "headings": {"en": title},
            "contents": {"en": message},
            "include_player_ids": oneSignalPushIds,
        }
        if subtitle:
            payload["subtitle"] = {"en": subtitle}

        response = requests.post(url, headers=headers, json=payload)
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Send Notification to User Response (raw): {response.text}")
            response.raise_for_status()
        logger.info(f"Send Notification to User Response: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Error sending notification to user: {e}")
        return {"error": str(e)}


# Subscribe to a channel
def subscribe_to_channel(device_token: str, channel_tag: str):
    url = f"https://onesignal.com/api/v1/players/{device_token}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    payload = {"app_id": ONESIGNAL_APP_ID, "tags": {channel_tag: "subscribed"}}
    response = requests.put(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Subscribe to Channel Response (raw): {response.text}")
        response.raise_for_status()
    logger.info(f"Subscribe to Channel Response: {response_data}")
    return response


# Unsubscribe from a channel
def unsubscribe_from_channel(device_token: str, channel_tag: str):
    url = f"https://onesignal.com/api/v1/players/{device_token}"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    payload = {"app_id": ONESIGNAL_APP_ID, "tags": {channel_tag: ""}}
    response = requests.put(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Unsubscribe from Channel Response (raw): {response.text}")
        response.raise_for_status()
    logger.info(f"Unsubscribe from Channel Response: {response_data}")
    return response


# Send a notification to a channel
def send_notification_to_channel(title: str, message: str, channel_tag: str = None):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message},
    }
    if channel_tag:
        payload["filters"] = [
            {"field": "tag", "key": channel_tag, "relation": "=", "value": "subscribed"}
        ]
    response = requests.post(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Send Notification Response (raw): {response.text}")
        response.raise_for_status()
    logger.info(f"Send Notification Response: {response_data}")
    return response


# Cancel a scheduled notification
def cancel_scheduled_notification(notification_id: str):
    try:
        url = f"https://onesignal.com/api/v1/notifications/{notification_id}?app_id={ONESIGNAL_APP_ID}"
        headers = {"Authorization": f"Basic {ONESIGNAL_API_KEY}"}
        response = requests.delete(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error canceling notification: {response.json()}")
            return response.json()

        return {"message": "Notification canceled successfully"}
    except Exception as e:
        logger.error(f"Error canceling notification: {e}")
        return {"error": str(e)}


# Store a daily notification
def store_daily_notification(
    user_id: str,
    hour: int,
    minute: int,
    title: str,
    message: str,
    pet_name: str,
    subtitle: str = None,
):
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            logger.error(f"User not found: {user_id}")
            return {"error": "User not found"}

        user_data = user_doc.to_dict()

        # Cancel any existing scheduled notification
        existing_notification_id = user_data.get("daily_playtime_reminder", {}).get(
            "notification_id"
        )
        if existing_notification_id:
            cancel_response = cancel_scheduled_notification(existing_notification_id)
            if "error" in cancel_response:
                return cancel_response

        # Store notification details in Firestore
        user_ref.set(
            {
                "daily_playtime_reminder": {
                    "hour": hour,
                    "minute": minute,
                    "title": title,
                    "message": message,
                    "subtitle": subtitle,
                    "pet_name": pet_name,
                }
            },
            merge=True,
        )

        return {"message": "Notification scheduled successfully"}
    except Exception as e:
        logger.error(f"Error storing notification: {e}")
        return {"error": str(e)}


# Send daily notification
def send_daily_notification(
    title: str, message: str, user_ids: list, subtitle: str = None
):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message},
        "include_player_ids": user_ids,
    }
    if subtitle:
        payload["subtitle"] = {"en": subtitle}

    response = requests.post(url, headers=headers, json=payload)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Send Notification Response (raw): {response.text}")
        response.raise_for_status()
    logger.info(f"Send Notification Response: {response_data}")
    return response
