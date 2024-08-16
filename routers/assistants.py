import os

from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field

from assistants.agents import ask_dogy, retrieve_assistant
from assistants.threads import create_thread
from assistants.types import UserMessage

router = APIRouter(prefix="/assistants")


class ThreadResponse(BaseModel):
    thread_id: str = Field(..., example="thread_ARIh2AxQdvhc1LGQL0MoOQ2v")


class DogyResponse(BaseModel):
    response: str = Field(..., example="Hi, how may I help you?")
    assistant_id: str = Field(..., example="asst_94p7EXxWvmiwWW7XlPowOP67")
    thread_id: str = Field(..., example="thread_ARIh2AxQdvhc1LGQL0MoOQ2v")
    assistant_selected: str = Field(..., example="nutrition_assistant")


@router.post("/threads", response_model=ThreadResponse)
async def create_thread_endpoint():
    """
    Create a new thread for the conversation.

    Returns:
        thread_id (`str`): The thread ID

    Raises:
        `HTTPException`: Raises HTTP 500 if any error happened
    """
    try:
        response = await create_thread()
        return JSONResponse(content=response)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/run", response_model=DogyResponse)
async def dogy_assistant(user_message: UserMessage):
    """
    Ask Dogy a question. On your first run, there is no need to provide a thread
    ID, but after that, you need to provide the thread ID of the previous
    conversation to save the history context.

    Args:
        user_message (`UserMessage`): The user message

    Returns:
        response (`str`): The response from Dogy
        assistant_selected (`str`): The assistant selected (For internal debugging only)
        assistant_id (`str`): The assistant ID (For internal debugging only)
        thread_id (`str`): The thread ID (Use this after the first run)

    Raises:
        `HTTPException`: Raises HTTP 500 if any error happened
    """
    try:
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
            raise HTTPException(
                status_code=500, detail="Assistant ID failed to retrieve"
            )

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

        return JSONResponse(
            content={
                "response": response,
                "assistant_selected": selected_assistant,
                "assistant_id": assistant_id,
                "thread_id": user_message.thread_id,
            }
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
