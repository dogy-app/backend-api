from google.cloud.firestore import ArrayUnion
from utils.firebase import db

from .core import logger


def register_device(user_id: str, one_signal_push_id: str):
    try:
        # Register device in the database
        user_ref = db.collection("users").document(user_id)
        user_ref.update({"pushIDs": ArrayUnion([one_signal_push_id])})
        logger.info(f"Device registered successfully for user: {user_id}")
        return {"message": "Device registered successfully"}
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        return {"error": str(e)}
