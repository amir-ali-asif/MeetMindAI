import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)


def translate_to_english(transcript_text: str) -> dict:
    """
    Translates a transcript into clear English. Works for:
    - ElevenLabs output (Hindi script + English mixed)
    - Speechmatics output (Urdu script + English mixed)

    This is used before passing the transcript to the LLM for 
    summary/action item extraction, since the extraction model 
    performs most reliably on English input.
    """
    try:
        response = llm.invoke([
            ("system", """You are a translator. Translate the following meeting transcript 
into clear, natural English. It may contain a mix of Urdu, Hindi, and English.

Rules:
- Preserve all names, numbers, dates, and technical terms exactly as they are.
- Do not add commentary or explanation, only return the translated transcript.
- Keep speaker labels if present (e.g. "Ahmed:", "Sara:")."""),
            ("human", transcript_text)
        ])

        return {
            "success": True,
            "text": response.content,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": None,
            "error": str(e)
        }


def transliterate_hindi_to_urdu(hindi_text: str) -> dict:
    """
    Converts Devanagari-script Hindi text into Urdu (Nastaliq) script.
    This is ONLY needed for ElevenLabs output, since ElevenLabs 
    transcribes Urdu speech using Hindi script. Speechmatics already 
    outputs correct Urdu script, so this function is never called 
    for Speechmatics transcripts.

    This is a script conversion, not a translation - spoken Hindi 
    and Urdu are the same language, just written differently.
    """
    try:
        response = llm.invoke([
            ("system", """You will receive text written in Devanagari (Hindi script). 
Convert it into Urdu script (Nastaliq/Perso-Arabic script), preserving the exact 
same words and meaning - this is a script transliteration, not a translation, 
since Hindi and Urdu are the same spoken language written in different scripts.

Rules:
- Do not translate the meaning or change any words - only convert the script.
- Keep names, numbers, and technical terms as they would naturally appear in Urdu script.
- Preserve speaker labels if present (e.g. "Ahmed:", "Sara:").
- Return ONLY the converted text, no explanation."""),
            ("human", hindi_text)
        ])

        return {
            "success": True,
            "text": response.content,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "text": None,
            "error": str(e)
        }