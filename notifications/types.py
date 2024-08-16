from pydantic import BaseModel


class DeviceRegistration(BaseModel):
    user_id: str
    oneSignalPushId: str


class ChannelSubscription(BaseModel):
    device_token: str
    channel_tag: str


class NotificationMessage(BaseModel):
    title: str
    message: str
    channel_tag: str = None


class UserNotification(BaseModel):
    title: str
    message: str
    user_id: str
    subtitle: str = None


class NotificationSchedule(BaseModel):
    user_id: str
    hour: int
    minute: int
    title: str
    message: str
    pet_name: str
    subtitle: str = None


class CancelNotification(BaseModel):
    notification_id: str
