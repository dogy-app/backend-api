import os

from openai import AsyncOpenAI
from openai.types.beta import Thread


async def create_thread():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    thread: Thread = await client.beta.threads.create()
    return {"thread_id": thread.id}
