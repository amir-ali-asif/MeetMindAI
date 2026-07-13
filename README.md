# Urdu-English Meeting Execution Assistant

## Introduction

This project is an AI-powered meeting intelligence tool built specifically for 
Urdu-English multilingual meetings — the way teams in Pakistan actually talk, 
mixing both languages naturally within the same conversation, even the same sentence.

Unlike existing meeting assistants (Otter, Read AI, Sembly, Fireflies) which are 
built around single-language, mostly English speech, this tool is designed from 
the ground up to handle Urdu-English code-switching accurately, and to turn 
meetings into actual execution — not just transcripts and summaries.

The tool records or accepts meeting audio, transcribes it accurately across both 
languages, extracts a summary and clear action items with owners and deadlines, 
and automatically pushes those action items into tools like Gmail and Notion — 
closing the loop between "what was said" and "what actually gets done."

## Tech Stack

- **Transcription (Speech-to-Text):** ElevenLabs Scribe v2 (primary), Speechmatics 
  Enhanced model (automatic fallback if the primary provider fails)
- **Language Model Framework:** LangChain (with structured output via Pydantic), 
  using Groq API Key and model -> llama-3.3-70b-versatile
- **Integrations:** Gmail API, Notion API
- **Backend:** Python
- **Frontend:** Streamlit
- **Version Control:** Git + GitHub

## Progress Log

### Step 1: Evaluated transcription models
Tested Speechmatics, Soniox, and ElevenLabs Scribe v2 on real Urdu-English 
meeting audio clips, comparing accuracy against a manually written ground-truth 
transcript. Selected **ElevenLabs Scribe v2** as the primary transcription 
engine based on strong accuracy, particularly on numeric figures.

### Step 2: Set up GitHub repository and project structure
Created the GitHub repository, connected the local project folder, added a 
`.gitignore` to exclude API keys and audio files from version control, and 
set up the base folder structure (`src/`, `sample_audio/`).

### Step 3: Built `transcribe.py` — core transcription function
Built a reusable `transcribe_audio()` function using the ElevenLabs Scribe v2 
API, with speaker diarization enabled and proper error handling.

### Step 4: Added Speechmatics as an automatic fallback
Built a secondary `transcribe_speechmatics()` function using Speechmatics' 
Enhanced model. Updated `transcribe_audio()` so that if ElevenLabs fails for 
any reason (credits exhausted, network error, etc.), the system automatically 
switches to Speechmatics, ensuring meetings are never left untranscribed.

### Step 5: Cleaned up error handling for user-facing messages
Replaced raw exception/error dumps with simple, human-readable status messages 
(e.g., "There is some error in ElevenLabs, so we are doing it with Speechmatics") 
so the tool feels polished and demo-ready rather than exposing technical logs.

### Step 6: Built LLM-based summary and action item extraction using LangChain
Used LangChain with a Pydantic schema (`MeetingAnalysis`, `ActionItem`) to 
enforce structured output from llama-3.3-70b-versatile, avoiding manual JSON parsing. Each 
action item includes a confidence score — flagging cases where the owner or 
deadline was unclear in the transcript, so these can be confirmed by a human 
instead of silently misassigned.

### Step 7 (revised): Separated translation logic into its own module
Split translation and transliteration logic out of `summarize.py` into a 
dedicated `translate.py` file, with two functions: `translate_to_english()` 
(converts Urdu/Hindi/English mixed transcripts into English for LLM 
processing) and `transliterate_hindi_to_urdu()` (converts ElevenLabs' 
Hindi-script output into correct Urdu script for display, since 
Speechmatics already outputs Urdu script natively).

### Step 8: Improved action item owner attribution
Updated the extraction prompt so that when a person's name isn't clearly 
mentioned in the transcript, the action item falls back to the speaker 
label (e.g. "Speaker 1") instead of being left unassigned. This ensures 
every action item has a traceable owner, while still marking these cases 
as low-confidence so they can be confirmed by a human before being 
auto-assigned in Jira/GitHub/Notion.

### Step 9: Built the Streamlit user interface
Created `app.py` with a Streamlit-based UI: users upload a meeting 
recording, and the app displays the original transcript (correct Urdu 
script), English translation, meeting summary, key decisions, and 
action items with confidence badges (high confidence vs needs human 
confirmation).

### Step 10: Added transcription model selector to UI
Added two buttons in the Streamlit UI (ElevenLabs, Speechmatics) letting 
users explicitly choose which speech-to-text provider to use, with 
accurate free-tier constraint information displayed for each. Defaults 
to ElevenLabs. Automatic fallback to the other provider still applies 
if the chosen one fails.