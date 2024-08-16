from fastapi import APIRouter, HTTPException

from notifications.channels import (
    send_notification_to_channel,
    subscribe_to_channel,
    unsubscribe_from_channel,
)
from notifications.devices import register_device
from notifications.schedule import (
    cancel_scheduled_notification,
    store_daily_notification,
)
from notifications.types import (
    CancelNotification,
    ChannelSubscription,
    DeviceRegistration,
    NotificationMessage,
    NotificationSchedule,
    UserNotification,
)
from notifications.users import send_notification_to_user

router = APIRouter(prefix="/notifications")


@router.post("/devices/register")
async def register_device_endpoint(device_registration: DeviceRegistration):
    response = register_device(
        device_registration.user_id, device_registration.oneSignalPushId
    )
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response


# Subscribe to a channel
@router.post("/channels/subscribe")
async def subscribe_to_channel_endpoint(subscription: ChannelSubscription):
    response = subscribe_to_channel(subscription.device_token, subscription.channel_tag)

    if response.status_code == 200:
        return {
            "message": "Subscribed to channel successfully",
            "response": response.json(),
        }
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Unsubscribe from a channel
@router.post("/channels/unsubscribe")
async def unsubscribe_from_channel_endpoint(subscription: ChannelSubscription):
    response = unsubscribe_from_channel(
        subscription.device_token, subscription.channel_tag
    )

    if response.status_code == 200:
        return {
            "message": "Unsubscribed from channel successfully",
            "response": response.json(),
        }
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Send a notification to a channel
@router.post("/channels/send")
async def send_notification_endpoint(notification: NotificationMessage):
    response = send_notification_to_channel(
        notification.title, notification.message, notification.channel_tag
    )

    if response.status_code == 200:
        return {
            "message": "Notification sent successfully",
            "response": response.json(),
        }
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Send a notification to a specific user
@router.post("/users/send")
async def send_notification_to_user_endpoint(user_notification: UserNotification):
    response = send_notification_to_user(
        user_notification.title,
        user_notification.message,
        user_notification.user_id,
        user_notification.subtitle,
    )

    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Notification sent to user successfully", "response": response}


# Schedule a daily notification
@router.post("/schedule/daily")
async def schedule_daily_notification(schedule: NotificationSchedule):
    response = store_daily_notification(
        schedule.user_id,
        schedule.hour,
        schedule.minute,
        schedule.title,
        schedule.message,
        schedule.pet_name,
        schedule.subtitle,
    )

    # Ensure response is a dictionary and check for 'error' key
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])

    # If response is not a dictionary, raise a different error
    if not isinstance(response, dict):
        raise HTTPException(
            status_code=500, detail="Invalid response from notification storage method."
        )

    return {"message": "Notification scheduled successfully", "response": response}


# Cancel a daily notification
@router.post("/schedule/cancel")
async def cancel_notification(cancel: CancelNotification):
    response = cancel_scheduled_notification(cancel.notification_id)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])

    return response
