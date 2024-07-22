import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import requests
import schedule
import time
import pytz
from firebase_setup import db
from google.cloud.firestore import ArrayUnion

load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

# Register a device for push notifications
def register_device(user_id: str, oneSignalPushId: str):
    try:
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'pushIDs': ArrayUnion([oneSignalPushId])
        })
        return {"message": "Device registered successfully"}
    except Exception as e:
        print("Error registering device:", e)
        return {"error": str(e)}

# Subscribe to a channel
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

# Unsubscribe from a channel
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

# Send a notification to a channel
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

# Send a notification to a user
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

# cancel a scheduled notification
def cancel_scheduled_notification(notification_id: str):
    try:
        url = f"https://onesignal.com/api/v1/notifications/{notification_id}?app_id={ONESIGNAL_APP_ID}"
        headers = {
            "Authorization": f"Basic {ONESIGNAL_API_KEY}"
        }
        response = requests.delete(url, headers=headers)

        if response.status_code != 200:
            print("Error canceling notification:", response.json())
            return response.json()

        return {"message": "Notification canceled successfully"}
    except Exception as e:
        print("Error canceling notification:", e)
        return {"error": str(e)}

# Schedule a daily notification
def schedule_daily_notification(user_id: str, hour: int, minute: int, title: str, message: str, pet_name: str, subtitle: str = None):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists():
            return {"error": "User not found"}
        user_data = user_doc.to_dict()
        oneSignalPushIds = user_data.get('pushIDs', [])
        user_timezone = user_data.get('timezone', 'UTC')

        if not oneSignalPushIds:
            return {"error": "No OneSignal Push IDs found for user"}

        # Cancel any existing scheduled notification
        existing_notification_id = user_data.get('daily_playtime_reminder', {}).get('notification_id')
        if existing_notification_id:
            cancel_response = cancel_scheduled_notification(existing_notification_id)
            if 'error' in cancel_response:
                return cancel_response

        now = datetime.now(pytz.timezone(user_timezone))
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if now > target_time:
            target_time += timedelta(days=1)

        notification_message = f"{message} {pet_name} today 🐾 !"

        notification_data = {
            "app_id": ONESIGNAL_APP_ID,
            "include_player_ids": oneSignalPushIds,
            "headings": {"en": title},
            "contents": {"en": notification_message},
            "send_after": target_time.isoformat(),
            "delayed_option": "timezone",
            "delivery_time_of_day": f"{hour:02d}:{minute:02d}",
            "ttl": 604800  # Time to live set to 7 days (7 * 24 * 60 * 60 seconds)
        }
        if subtitle:
            notification_data["subtitle"] = {"en": subtitle}

        print("Sending notification with data:", notification_data)  # Debug log

        response = requests.post("https://onesignal.com/api/v1/notifications", headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {ONESIGNAL_API_KEY}"
        }, json=notification_data)

        print("OneSignal response status:", response.status_code)  # Debug log
        print("OneSignal response data:", response.json())  # Debug log

        if response.status_code != 200:
            print("Error scheduling notification:", response.json())
            return response.json()

        # Store notification details in Firestore
        user_ref.set({
            'daily_playtime_reminder': {
                'hour': hour,
                'minute': minute,
                'title': title,
                'message': message,
                'subtitle': subtitle,
                'pet_name': pet_name,
                'notification_id': response.json().get("id")
            }
        }, merge=True)

        return response.json()
    except Exception as e:
        print("Error scheduling notification:", e)
        return {"error": str(e)}

# Daily notification job
def daily_notification_job():
    users_ref = db.collection('users')
    users = users_ref.stream()

    for user in users:
        user_data = user.to_dict()
        if 'daily_playtime_reminder' in user_data:
            reminder = user_data['daily_playtime_reminder']
            schedule_daily_notification(
                user.id,
                reminder['hour'],
                reminder['minute'],
                reminder['title'],
                reminder['message'],
                reminder['pet_name'],
                reminder.get('subtitle')
            )

# Schedule the job daily at midnight UTC
schedule.every().day.at("00:00").do(daily_notification_job)

while True:
    schedule.run_pending()
    time.sleep(1)
