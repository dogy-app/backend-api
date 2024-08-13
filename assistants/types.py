from pydantic import BaseModel
from typing import Optional


class UserMessage(BaseModel):
    user_message: str
    user_name: str
    thread_id: Optional[str] = None
