import requests
from utils.firebase import db

from .core import ONESIGNAL_API_KEY, ONESIGNAL_APP_ID, logger


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
