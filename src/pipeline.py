from transcribe import transcribe_audio
from summarize import extract_details

def process_meeting(audio_file_path: str) -> dict:
    transcription_result = transcribe_audio(audio_file_path)

    if not transcription_result["success"]:
        return {
            "success": False,
            "stage_failed": "transcription",
            "error": "Could not transcribe the audio."
        }

    transcript_text = transcription_result["text"]
    provider = transcription_result["provider_used"]

    llm_result = extract_details(transcript_text)

    if not llm_result["success"]:
        return {
            "success": False,
            "stage_failed": "summarization",
            "error": "Could not process the transcript into action items."
        }

    analysis = llm_result["data"]

    return {
        "success": True,
        "transcript": transcript_text,
        "transcription_provider": provider,
        "summary": analysis.summary,
        "key_decisions": analysis.key_decisions,
        "action_items": [item.model_dump() for item in analysis.action_items]  # convert to plain dicts for easy use later
    }


if __name__ == "__main__":
    test_file = "sample_audio/s2.ogg"
    result = process_meeting(test_file)

    if result["success"]:
        print(f"\n=== Transcribed via: {result['transcription_provider']} ===")
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