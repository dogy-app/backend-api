from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from starlette.responses import JSONResponse

from audio.speech_to_text import get_transcription

router = APIRouter(prefix="/audio")


class TranscriptionResponse(BaseModel):
    response: str


@router.post("/transcriptions")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Upload an audio file and get its transcription

    :param file: Audio file to transcribe
    :type file: UploadFile
    :return: Transcription of the audio file
    """

    try:
        # Get the filepath of the audio file and get its transcription
        transcription = get_transcription(file.filename)

        return JSONResponse(content={"response": transcription.text}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
