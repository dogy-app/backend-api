import os
from openai import OpenAI
from openai.types.audio.transcription import Transcription

def get_transcription(file_path: str) -> Transcription:
    """
    Get transcription of an audio file

    :param file_path: Path to the audio file
    :type file_path: str
    :return: Transcription of the audio file
    :rtype: Transcription
    """
    # Convert the audio file to readable binary
    audio_file = open(file_path, "rb")

    # Transcribe the audio file
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    # Returns: { text: transcripted }
    return transcription
