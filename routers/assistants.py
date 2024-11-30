from fastapi import APIRouter
from assistants.assistant import create_assistant, search_assistant, delete_assistant
from starlette.responses import JSONResponse
from fastapi import HTTPException, Query


router = APIRouter(prefix="/assistants")


@router.post("/")
def create_langgraph_assistant():
    """
    Create a new assistant
    """
    try:
        assistant = create_assistant()
        return JSONResponse(content=assistant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {e}")


@router.post("/search")
def search_langgraph_assistant():
    """
    Search for existing assistants
    """
    try:
        search_result = search_assistant()
        return JSONResponse(content=search_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching assistant: {e}")


@router.delete("/")
def delete_langgraph_assistant(assistant_id: str = Query(None)):
    """
    Search for existing assistants
    """
    try:
        response = delete_assistant(assistant_id)
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting assistant: {e}")
