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
- **Language Model (Summarization + Action Item Extraction):** OpenAI GPT-4o / 
  Anthropic Claude
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