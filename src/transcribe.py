import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from transcribe_speechmatics import transcribe_speechmatics

load_dotenv()

def _transcribe_elevenlabs(file_path: str) -> dict:
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        client = ElevenLabs(api_key=api_key)

        with open(file_path, "rb") as audio_file:
            result = client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v2",
                diarize=True
            )

        return {"success": True, "text": result.text, "error": None}

    except Exception as e:
        return {"success": False, "text": None, "error": str(e)}


def transcribe_audio(file_path: str, preferred_model: str = "elevenlabs") -> dict:
    """
    preferred_model: "elevenlabs" or "speechmatics" - the user's explicit choice.
    Still falls back to the other provider if the chosen one fails.
    """
    if preferred_model == "elevenlabs":
        result = _transcribe_elevenlabs(file_path)
        if result["success"]:
            result["provider_used"] = "elevenlabs"
            return result

        print("There is some error in ElevenLabs, so we are doing it with Speechmatics.")
        fallback_result = transcribe_speechmatics(file_path)
        if fallback_result["success"]:
            fallback_result["provider_used"] = "speechmatics"
            return fallback_result

    else:  # preferred_model == "speechmatics"
        result = transcribe_speechmatics(file_path)
        if result["success"]:
            result["provider_used"] = "speechmatics"
            return result

        print("There is some error in Speechmatics, so we are doing it with ElevenLabs.")
        fallback_result = _transcribe_elevenlabs(file_path)
        if fallback_result["success"]:
            fallback_result["provider_used"] = "elevenlabs"
            return fallback_result

    return {
        "success": False,
        "text": None,
        "provider_used": None,
        "error": "Both transcription providers failed."
    }