import os
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class ActionItem(BaseModel):
    task: str = Field(description="Clear description of the task")
    owner: Optional[str] = Field(description="Person's name if clearly stated, otherwise null")
    deadline: Optional[str] = Field(description="Deadline if clearly stated, otherwise null")
    confidence: str = Field(description="'high' or 'low' - use 'low' if owner or deadline was unclear")


class MeetingAnalysis(BaseModel):
    summary: str = Field(description="A clear, concise 3-5 sentence summary of the meeting")
    key_decisions: List[str] = Field(description="List of key decisions made in the meeting")
    action_items: List[ActionItem] = Field(description="List of action items extracted from the meeting")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)

structured_llm = llm.with_structured_output(MeetingAnalysis)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an assistant that processes transcripts of business meetings 
conducted in a mix of Urdu and English (as commonly spoken in Pakistan).

Rules:
- If an action item's owner is not clearly and explicitly stated, set owner to null and confidence to 'low'.
- If a deadline is vague (e.g. "soon", "later") rather than specific, set deadline to null and confidence to 'low'.
- Keep the summary and decisions in English, even if the original transcript mixes Urdu and English."""),
    ("human", "Here is the meeting transcript:\n\n{transcript}")
])

chain = prompt_template | structured_llm

def extract_details(transcript_text: str) -> dict:
    """
    Takes a transcript string and returns a dictionary with:
    summary, key_decisions, and action_items (with confidence scoring)
    """
    try:
        result: MeetingAnalysis = chain.invoke({"transcript": transcript_text})

        return {
            "success": True,
            "data": result,   # this is a Pydantic object, not a plain dict
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


if __name__ == "__main__":
    sample_transcript = """
    Ahmed: Theek hai, so humein deployment kal 5 PM tak complete karna hai.
    Sara: Haan, aur testing bhi parallel chalao please.
    Ahmed: Sure, main abhi start kar deta hoon.
    """

    result = extract_details(sample_transcript)

    if result["success"]:
        analysis = result["data"]
        print("=== Summary ===")
        print(analysis.summary)
        print("\n=== Key Decisions ===")
        for d in analysis.key_decisions:
            print(f"- {d}")
        print("\n=== Action Items ===")
        for item in analysis.action_items:
            print(f"- Task: {item.task}")
            print(f"  Owner: {item.owner} | Deadline: {item.deadline} | Confidence: {item.confidence}")
    else:
        print(f"Something went wrong: {result['error']}")