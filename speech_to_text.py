import os
from openai import OpenAI
from openai.types.audio.transcription import Transcription

def get_transcription(file_path) -> Transcription:
    audio_file = open(file_path, "rb")
    # Here you can add the code to process the audio file (e.g., speech-to-text)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    return transcription
