import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Notification(BaseModel):
    title: str
    body: str
    custom_data: dict = {}

AZURE_NOTIFICATION_HUB_CONNECTION_STRING = os.getenv("AZURE_NOTIFICATION_HUB_CONNECTION_STRING")
AZURE_NOTIFICATION_HUB_NAME = os.getenv("AZURE_NOTIFICATION_HUB_NAME")

async def register_device(device_token: str, platform: str, tags: list = None):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {AZURE_NOTIFICATION_HUB_CONNECTION_STRING}'
    }

    payload = {
        'Platform': platform.lower(),
        'RegistrationId': device_token,
        'Tags': tags or []
    }

    url = f'https://{AZURE_NOTIFICATION_HUB_NAME}.servicebus.windows.net/{AZURE_NOTIFICATION_HUB_NAME}/registrations/?api-version=2015-01'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

async def send_notification(device_token: str, platform: str, notification: Notification):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {AZURE_NOTIFICATION_HUB_CONNECTION_STRING}'
    }

    payload = {
        'notification': {
            'title': notification.title,
            'body': notification.body
        },
        'data': notification.custom_data
    }

    url = f'https://{AZURE_NOTIFICATION_HUB_NAME}.servicebus.windows.net/{AZURE_NOTIFICATION_HUB_NAME}/messages/?api-version=2015-01&direct={platform.lower()}'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
