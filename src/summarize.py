import os
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class ActionItem(BaseModel):
    task: str = Field(description="Clear description of the task")
    owner: Optional[str] = Field(
        description="Person's name if clearly and explicitly mentioned by name in the transcript. "
                    "If the name is unclear, not mentioned, or only identifiable by voice/speaker turn, "
                    "use the speaker label instead (e.g. 'Speaker 1', 'Speaker 2') exactly as it appears "
                    "in the transcript's diarization labels."
    )
    deadline: Optional[str] = Field(description="Deadline if clearly stated, otherwise null")
    confidence: str = Field(description="'high' if owner was identified by name, 'low' if identified only by speaker label or if deadline was vague")

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
conducted in a mix of Urdu and English (as commonly spoken in Pakistan). The transcript 
you receive has already been translated into English, and includes speaker labels 
(e.g. "Speaker 1:", "Speaker 2:", or names if they were mentioned in conversation).

Rules for identifying the owner of an action item:
- If a person's actual name is clearly and explicitly used in the transcript (e.g. "Ahmed will handle deployment"), use that name as the owner, and set confidence to 'high'.
- If no name is mentioned, but the task is clearly assigned to whoever is speaking or being addressed in a specific turn, use the speaker label exactly as it appears in the transcript (e.g. "Speaker 1", "Speaker 2") as the owner, and set confidence to 'low'.
- Never leave owner as null if a speaker label is available in the transcript - only use null if there is truly no way to tell who the task belongs to (e.g. no speaker labels at all, or the task wasn't clearly assigned to anyone).

Rules for deadlines:
- If a deadline is vague (e.g. "soon", "later") rather than specific, set deadline to null and confidence to 'low'.

Keep the summary and decisions in English."""),
    ("human", "Here is the meeting transcript:\n\n{transcript}")
])


chain = prompt_template | structured_llm


def extract_details(transcript_text: str) -> dict:
    """
    Takes an ENGLISH transcript (already translated) and returns:
    summary, key_decisions, and action_items (with confidence scoring)
    """
    try:
        result: MeetingAnalysis = chain.invoke({"transcript": transcript_text})

        return {
            "success": True,
            "data": result,
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
    Ahmed: Acha humein deployment kal 5 bajay tak complete krna hai.
    Sara: Yes, and please run testing in parallel.
    Ahmed: Sure, I'll start abhi se hi.
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