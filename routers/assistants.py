import os

from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from starlette.responses import JSONResponse

from assistants.agents import ask_dogy, retrieve_assistant
from assistants.threads import create_thread
from assistants.types import UserMessage

router = APIRouter(prefix="/assistants")


@router.post("/threads")
async def create_thread_endpoint():
    try:
        response = await create_thread()
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/run")
async def dogy_assistant(user_message: UserMessage):
    """
    Ask Dogy a question. Use the same assistant ID and thread ID for the same
    conversation.

    :param user_message: User message and user name. Optionally, you can provide
    the assistant ID and thread ID to continue the conversation.
    :return: Dogy's response, assistant ID, and thread ID.
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    selected_assistant = await retrieve_assistant(user_message.user_message)
    print(selected_assistant)

    dogy_id = os.getenv("DOGY_COMPANION_ID")
    nutrition_assistant_id = os.getenv("NUTRITION_ASSISTANT_ID")

    if selected_assistant == "none":
        assistant_id = dogy_id
    elif selected_assistant == "nutrition_assistant":
        assistant_id = nutrition_assistant_id
    else:
        raise HTTPException(status_code=500, detail="Assistant ID failed to retrieve")

    await client.beta.assistants.retrieve(assistant_id=assistant_id)
    if not user_message.thread_id:
        ids = await create_thread()
        user_message.thread_id = ids["thread_id"]

    print(f"Assistant ID: {assistant_id}")
    print(f"Thread ID: {user_message.thread_id}")
    response = await ask_dogy(
        user_message.user_message,
        user_message.user_name,
        assistant_id,
        user_message.thread_id,
    )

    return {
        "response": response,
        "assistant_selected": selected_assistant,
        "assistant_id": assistant_id,
        "thread_id": user_message.thread_id,
    }
