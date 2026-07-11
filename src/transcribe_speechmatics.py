import os
import asyncio
from dotenv import load_dotenv
from speechmatics.batch import AsyncClient, TranscriptionConfig

load_dotenv()

async def _transcribe_speechmatics_async(file_path: str) -> dict:
    try:
        client = AsyncClient()  # reads SPEECHMATICS_API_KEY from environment
        config = TranscriptionConfig(
            language="ur",
            model="enhanced",
            diarization="speaker"
        )
        result = await client.transcribe(file_path, transcription_config=config)
        await client.close()

        return {
            "success": True,
            "text": result.transcript_text,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": None,
            "error": str(e)
        }


def transcribe_speechmatics(file_path: str) -> dict:
    """Synchronous wrapper so this matches the same interface as ElevenLabs function"""
    return asyncio.run(_transcribe_speechmatics_async(file_path))