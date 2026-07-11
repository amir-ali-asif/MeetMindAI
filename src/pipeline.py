from transcribe import transcribe_audio
from translate import translate_to_english, transliterate_hindi_to_urdu
from summarize import extract_details


def process_meeting(audio_file_path: str) -> dict:
    """
    Full pipeline: audio file -> transcript -> (transliterate if needed) 
    -> translate to English -> summary + action items
    """

    # Step 1: Transcribe
    transcription_result = transcribe_audio(audio_file_path)

    if not transcription_result["success"]:
        return {
            "success": False,
            "stage_failed": "transcription",
            "error": "Could not transcribe the audio."
        }

    raw_transcript = transcription_result["text"]
    provider = transcription_result["provider_used"]

    # Step 2: If ElevenLabs was used, transliterate Hindi script -> Urdu script for display
    if provider == "elevenlabs":
        translit_result = transliterate_hindi_to_urdu(raw_transcript)
        display_transcript = translit_result["text"] if translit_result["success"] else raw_transcript
    else:
        # Speechmatics already outputs correct Urdu script
        display_transcript = raw_transcript

    # Step 3: Translate original transcript to English (for the LLM extraction step)
    translation_result = translate_to_english(raw_transcript)

    if not translation_result["success"]:
        return {
            "success": False,
            "stage_failed": "translation",
            "error": "Could not translate the transcript to English."
        }

    english_transcript = translation_result["text"]

    # Step 4: Extract summary + action items from the English transcript
    llm_result = extract_details(english_transcript)

    if not llm_result["success"]:
        return {
            "success": False,
            "stage_failed": "summarization",
            "error": "Could not process the transcript into action items."
        }

    analysis = llm_result["data"]

    return {
        "success": True,
        "display_transcript": display_transcript,     # correct Urdu script, show in UI
        "english_transcript": english_transcript,      # used for debugging/comparison
        "transcription_provider": provider,
        "summary": analysis.summary,
        "key_decisions": analysis.key_decisions,
        "action_items": [item.model_dump() for item in analysis.action_items]
    }


if __name__ == "__main__":
    test_file = "sample_audio/s1.ogg"
    result = process_meeting(test_file)

    if result["success"]:
        print(f"\n=== Transcribed via: {result['transcription_provider']} ===")
        print(f"\n=== Original Transcript (Urdu script) ===\n{result['display_transcript']}")
        print(f"\n=== English Translation ===\n{result['english_transcript']}")
        print(f"\n=== Summary ===\n{result['summary']}")
        print(f"\n=== Key Decisions ===")
        for d in result["key_decisions"]:
            print(f"- {d}")
        print(f"\n=== Action Items ===")
        for item in result["action_items"]:
            print(f"- Task: {item['task']}")
            print(f"  Owner: {item['owner']} | Deadline: {item['deadline']} | Confidence: {item['confidence']}")

        low_confidence_items = [item for item in result["action_items"] if item["confidence"] == "low"]
        if low_confidence_items:
            print(f"\n⚠️  {len(low_confidence_items)} action item(s) need human confirmation (unclear owner/deadline).")
    else:
        print(f"Pipeline failed at: {result['stage_failed']} — {result['error']}")