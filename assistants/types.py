from typing import Optional

from pydantic import BaseModel


class UserMessage(BaseModel):
    user_message: str
    user_name: str
    thread_id: Optional[str] = None
