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

        return {
            "success": True,
            "text": result.text,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": None,
            "error": str(e)
        }


def transcribe_audio(file_path: str) -> dict:
    """
    Tries ElevenLabs first (primary model).
    If it fails for ANY reason (credits exhausted, network error, etc.),
    automatically falls back to Speechmatics.
    Returns which provider actually produced the result, for transparency.
    """
    result = _transcribe_elevenlabs(file_path)

    if result["success"]:
        result["provider_used"] = "elevenlabs"
        return result

    print("There is some error in ElevenLabs, so we are doing it with Speechmatics.")
    fallback_result = transcribe_speechmatics(file_path)

    if fallback_result["success"]:
        fallback_result["provider_used"] = "speechmatics"
        return fallback_result

    # Both failed
    print("Speechmatics also failed. Unable to transcribe this audio right now.")
    return {
        "success": False,
        "text": None,
        "provider_used": None,
        "error": "Both transcription providers failed."
    }

if __name__ == "__main__":
    test_file = "sample_audio/s2.ogg"
    output = transcribe_audio(test_file)

    if output["success"]:
        print(f"\n=== TRANSCRIPT (via {output['provider_used']}) ===")
        print(output["text"])
    else:
        print("Sorry, transcription failed. Please try again later.")