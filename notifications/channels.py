from .core import logger, ONESIGNAL_API_KEY, ONESIGNAL_APP_ID
import requests


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
