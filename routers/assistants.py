from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from assistants.agents import inference_completion, inference_completion_sse
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
        response = await inference_completion(user_message)
        return JSONResponse(content=response)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/run/sse", response_model=DogyResponse)
async def dogy_assistant_sse(user_message: UserMessage):
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
        return StreamingResponse(inference_completion_sse(user_message))
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
