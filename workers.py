import logging
import threading
import time
from datetime import datetime, timedelta

import pytz
import schedule
from dotenv import load_dotenv
from notifications.schedule import send_daily_notification
from utils.firebase import db

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"


def daily_notification_job():
    logger.info("Checking for notifications to send...")
    try:
        users_ref = db.collection("users")
        users = users_ref.stream()

        for user in users:
            user_data = user.to_dict()
            if "daily_playtime_reminder" in user_data:
                reminder = user_data["daily_playtime_reminder"]
                timezone_str = user_data.get("timezone", "UTC")
                user_timezone = pytz.timezone(timezone_str)
                logger.info(
                    f"Processing user {user.id} with reminder {reminder} in timezone {timezone_str}"
                )
                user_id = user.id
                user_ref = db.collection("users").document(user_id)
                push_ids = user_data.get("pushIDs", [])
                if push_ids:
                    now = datetime.now(user_timezone)
                    reminder_time = now.replace(
                        hour=reminder["hour"],
                        minute=reminder["minute"],
                        second=0,
                        microsecond=0,
                    )
                    if now > reminder_time:
                        reminder_time += timedelta(days=1)

                    time_to_send = reminder_time - now

                    last_sent = user_data.get("last_notification_sent", None)
                    if last_sent:
                        last_sent_time = datetime.fromisoformat(last_sent)
                    else:
                        last_sent_time = None

                    if last_sent_time and last_sent_time.date() == now.date():
                        logger.info(
                            f"Notification for user {user_id} already sent today."
                        )
                    elif (
                        time_to_send.total_seconds() <= 60
                    ):  # Send the notification if it's within the next minute
                        logger.info(
                            f"Notification for user {user_id} should go out now: {format_timedelta(time_to_send)} left"
                        )
                        send_daily_notification(
                            reminder["title"],
                            f"{reminder['message']} {reminder['pet_name']} today 🐾 !",
                            push_ids,
                            reminder.get("subtitle"),
                        )
                        user_ref.update({"last_notification_sent": now.isoformat()})
                    else:
                        logger.info(
                            f"Notification for user {user_id} is scheduled in: {format_timedelta(time_to_send)}"
                        )
                else:
                    logger.warning(f"No push IDs found for user {user_id}")
            else:
                logger.warning(f"No daily_playtime_reminder found for user {user.id}")
    except Exception as e:
        logger.error(f"Error running daily_notification_job: {e}")


def run_scheduler():
    logger.info("Starting scheduler")
    schedule.every(1).minutes.do(daily_notification_job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    logger.info("Worker started and running")

    while True:
        logger.info("Worker is alive...")
        time.sleep(300)  # Log every 5 minutes to show the worker is running
