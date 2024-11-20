import requests

from utils.firebase import db

from .core import ONESIGNAL_API_KEY, ONESIGNAL_APP_ID, logger


# Send a notification to a user
def send_notification_to_user(
    title: str, message: str, user_id: str, subtitle: str = None, data: dict = None
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
        if data:
            payload["data"] = data

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
