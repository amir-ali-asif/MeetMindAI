# 🎙️ MeetMindAI: Urdu-English Meeting Execution Assistant

An AI-powered meeting intelligence tool built specifically for **Urdu-English
multilingual meetings** — the way teams in Pakistan actually talk, mixing both
languages naturally within the same conversation, even the same sentence.

Unlike existing meeting assistants (Otter, Read AI, Sembly, Fireflies) which
are built around single-language, mostly English speech, this tool is
designed from the ground up to handle Urdu-English code-switching accurately,
and to turn meetings into actual **execution** — not just transcripts and
summaries.

The tool accepts meeting audio, transcribes it accurately across both
languages, extracts a summary and clear action items with owners and
deadlines, and pushes a polished report straight to any email address you
provide — closing the loop between "what was said" and "what actually gets
done."

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone the repository](#2-clone-the-repository)
  - [3. Set up a virtual environment](#3-set-up-a-virtual-environment)
  - [4. Install dependencies](#4-install-dependencies)
  - [5. Configure API keys](#5-configure-api-keys--env)
  - [6. Set up Gmail SMTP access](#6-set-up-gmail-smtp-access-for-report-emails)
  - [7. Run the app](#7-run-the-app)
- [Usage Guide](#usage-guide)
- [Build Log — How This Project Was Built](#build-log--how-this-project-was-built)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Features

- 🎧 **Dual transcription engines** — ElevenLabs Scribe v2 (primary) with
  automatic fallback to Speechmatics Enhanced, so a meeting is never left
  untranscribed.
- 🗣️ **Speaker diarization** on both providers, so action items can be traced
  back to a specific speaker even when no name is mentioned.
- 🔤 **Correct Urdu-script display** — automatically transliterates
  ElevenLabs' Hindi-script (Devanagari) output into proper Urdu (Nastaliq)
  script for display, since Speechmatics already outputs Urdu natively.
- 🌐 **Code-switch-aware translation** — converts mixed Urdu/Hindi/English
  transcripts into clean English before analysis, preserving names, numbers,
  dates, and speaker labels.
- 🧠 **Structured summary & action-item extraction** via an LLM constrained
  to a strict Pydantic schema — no manual JSON parsing, no hallucinated
  fields.
- ✅ **Confidence-scored ownership** — every action item is either
  confidently assigned to a named person or transparently flagged as "needs
  human confirmation" (assigned to a speaker label instead of being lost).
- 📄 **One-click PDF report generation** with a clean summary, key decisions,
  and an action-items table.
- 📧 **Send-to-any-email delivery** — the user enters a recipient email
  address directly in the UI, and the report is emailed to that address via
  Gmail SMTP — no hardcoded recipient, no OAuth consent flow.
- 🖥️ **Simple Streamlit UI** — upload, choose your transcription engine,
  process, review, and send — no command-line steps required after setup.

## Tech Stack

| Layer | Technology |
|---|---|
| Speech-to-Text | ElevenLabs Scribe v2 (primary), Speechmatics Enhanced model (automatic fallback) |
| LLM Framework | LangChain, structured output via Pydantic |
| LLM Provider | Groq API (`openai/gpt-oss-120b`) |
| Report Generation | ReportLab (PDF) |
| Email Delivery | Gmail SMTP (App Password) |
| Backend | Python |
| Frontend | Streamlit |
| Version Control | Git + GitHub |

## How It Works

```
Audio file
   │
   ▼
[1] Transcribe  ──────────────► ElevenLabs Scribe v2 (default)
   │                                   │ on failure
   │                                   ▼
   │                            Speechmatics Enhanced (fallback)
   ▼
[2] Transliterate (ElevenLabs output only)
    Hindi/Devanagari script → Urdu/Nastaliq script (for display)
   ▼
[3] Translate raw transcript → English
    (mixed Urdu/Hindi/English → clean English, for the LLM step)
   ▼
[4] Extract summary + key decisions + action items (LLM, structured output)
    Each action item: task, owner, deadline, confidence
   ▼
[5] Display in Streamlit UI
    (original Urdu transcript, English translation, summary, action items)
   ▼
[6] (Optional) Generate PDF report → Email to a recipient address entered
    by the user, via Gmail SMTP
```

## Project Structure

```
meeting-assistant/
├── app.py                        # Streamlit UI — upload, process, review, send
├── requirements.txt               # Python dependencies
├── src/
│   ├── pipeline.py                # Orchestrates the end-to-end flow
│   ├── transcribe.py              # ElevenLabs transcription + fallback logic
│   ├── transcribe_speechmatics.py # Speechmatics transcription (async client)
│   ├── translate.py               # Translation + Hindi→Urdu transliteration
│   ├── summarize.py               # LLM-based summary & action item extraction
│   ├── pdf_generator.py           # Builds the PDF meeting report
│   └── email_sender.py            # Sends the report via Gmail SMTP
├── temp_uploads/                  # Uploaded audio files (gitignored, auto-created)
├── reports/                       # Generated PDF reports (gitignored, auto-created)
└── .gitignore
```

## Getting Started

### 1. Prerequisites

- Python 3.10 or later
- API keys / accounts for:
  - [ElevenLabs](https://elevenlabs.io/) (Scribe v2 speech-to-text)
  - [Speechmatics](https://www.speechmatics.com/) (Enhanced model, fallback transcription)
  - [Groq](https://groq.com/) (LLM inference — translation, transliteration, extraction)
- A Gmail account with an **App Password** enabled, if you want to use
  the "Send Report" email feature (see [step 6](#6-set-up-gmail-smtp-access-for-report-emails))

### 2. Clone the repository

```bash
git clone <your-repository-url>
cd meeting-assistant
```

### 3. Set up a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API keys (`.env`)

Create a `.env` file in the project root (this file is gitignored and should
never be committed):

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
SPEECHMATICS_API_KEY=your_speechmatics_api_key
GROQ_API_KEY=your_groq_api_key
GMAIL_ADDRESS=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password
```

| Variable | Used by | Purpose |
|---|---|---|
| `ELEVENLABS_API_KEY` | `src/transcribe.py` | Primary transcription engine |
| `SPEECHMATICS_API_KEY` | `src/transcribe_speechmatics.py` | Fallback (or manually selected) transcription engine |
| `GROQ_API_KEY` | `src/translate.py`, `src/summarize.py` | LLM calls for translation, transliteration, and extraction |
| `GMAIL_ADDRESS` | `src/email_sender.py` | The Gmail account the report is sent **from** |
| `GMAIL_APP_PASSWORD` | `src/email_sender.py` | App password authenticating that Gmail account for SMTP |

> Note: the report's **recipient** is not an environment variable — it's
> whatever email address the user types into the app's "Send Report" field
> at runtime.

### 6. Set up Gmail SMTP access (for report emails)

The "Send Report" feature sends mail via Gmail's SMTP server using an app
password — no OAuth consent screen and no browser popup required, so it
works the same way locally and on a deployed server.

1. Enable **2-Step Verification** on the Gmail account you want to send
   from, at [myaccount.google.com/security](https://myaccount.google.com/security)
   (app passwords only exist for accounts with this on).
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   and generate a new app password (e.g. name it "meeting assistant").
3. Copy the 16-character code Google gives you and set it as
   `GMAIL_APP_PASSWORD` in your `.env` (remove any spaces).
4. Set `GMAIL_ADDRESS` to the Gmail address you generated the app password
   for.

> This is **not** your normal Gmail login password — Google blocks
> password-based SMTP login entirely for accounts with 2-Step Verification
> on. The app password is a separate, single-purpose credential.

### 7. Run the app

```bash
streamlit run app.py
```

Streamlit will print a local URL (typically `http://localhost:8501`) —
open it in your browser to use the app.

## Usage Guide

1. **Choose a transcription engine** — ElevenLabs or Speechmatics. ElevenLabs
   is selected by default; if it fails for any reason (e.g. quota exhausted,
   network error), the app automatically retries with the other provider.
2. **Upload a meeting recording** — supported formats: `.wav`, `.mp3`,
   `.m4a`, `.ogg`. Both transcription providers are running on free-tier
   limits in this demo, so a short clip (1-2 minutes) is best for trying the
   project out.
3. **Click "Process Meeting"** — the app transcribes the audio, converts the
   script for correct Urdu display, translates it to English, and runs LLM
   extraction. This produces:
   - The original transcript in correct Urdu script
   - An English translation
   - A concise meeting summary
   - A list of key decisions
   - A list of action items, each with a task, owner, deadline, and a
     confidence badge (🟢 high confidence / 🟡 needs human confirmation)
4. **Review the action items** — items marked 🟡 mean the owner or deadline
   wasn't explicitly stated and was inferred from a speaker label; confirm
   these before treating them as final.
5. **Enter a recipient email and click "Send Report"** — generates a PDF of
   the summary, key decisions, and action items table, and emails it to
   whatever address you type into the field.

## Build Log — How This Project Was Built

### Step 1: Evaluated transcription models
Tested Speechmatics, Soniox, and ElevenLabs Scribe v2 on real Urdu-English
meeting audio clips, comparing accuracy against a manually written
ground-truth transcript. Selected **ElevenLabs Scribe v2** as the primary
transcription engine based on strong accuracy, particularly on numeric
figures.

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
Replaced raw exception/error dumps with simple, human-readable status
messages (e.g., "There is some error in ElevenLabs, so we are doing it with
Speechmatics") so the tool feels polished and demo-ready rather than exposing
technical logs.

### Step 6: Built LLM-based summary and action item extraction using LangChain
Used LangChain with a Pydantic schema (`MeetingAnalysis`, `ActionItem`) to
enforce structured output from `openai/gpt-oss-120b` on Groq, avoiding manual
JSON parsing. Each action item includes a confidence score — flagging cases
where the owner or deadline was unclear in the transcript, so these can be
confirmed by a human instead of silently misassigned.

### Step 7 (revised): Separated translation logic into its own module
Split translation and transliteration logic out of `summarize.py` into a
dedicated `translate.py` file, with two functions: `translate_to_english()`
(converts Urdu/Hindi/English mixed transcripts into English for LLM
processing) and `transliterate_hindi_to_urdu()` (converts ElevenLabs' Hindi-
script output into correct Urdu script for display, since Speechmatics
already outputs Urdu script natively).

### Step 8: Improved action item owner attribution
Updated the extraction prompt so that when a person's name isn't clearly
mentioned in the transcript, the action item falls back to the speaker label
(e.g. "Speaker 1") instead of being left unassigned. This ensures every
action item has a traceable owner, while still marking these cases as
low-confidence so they can be confirmed by a human before being auto-assigned
in Jira/GitHub/Notion.

### Step 9: Built the Streamlit user interface
Created `app.py` with a Streamlit-based UI: users upload a meeting recording,
and the app displays the original transcript (correct Urdu script), English
translation, meeting summary, key decisions, and action items with confidence
badges (high confidence vs needs human confirmation).

### Step 10: Added transcription model selector to UI
Added two buttons in the Streamlit UI (ElevenLabs, Speechmatics) letting
users explicitly choose which speech-to-text provider to use, with accurate
free-tier constraint information displayed for each. Defaults to ElevenLabs.
Automatic fallback to the other provider still applies if the chosen one
fails.

### Step 11: Added PDF report generation and email delivery
Built `pdf_generator.py` using ReportLab to create a clean, professional
meeting report (summary, key decisions, action items table). Added
`send_meeting_report_email()` to email this PDF as an attachment. Wired both
into the pipeline via a "Send Report to CEO" button in the UI — completing
the core "meeting to execution" loop end-to-end.

### Step 12: Switched to a user-entered recipient with Gmail SMTP
Replaced the hardcoded `CEO_EMAIL` recipient with a text input in the UI, so
the report can be sent to any address the user provides. Also replaced the
Gmail API OAuth flow (`InstalledAppFlow`, `credentials.json`, `token.json`)
with plain Gmail SMTP authenticated via an app password — the OAuth flow
required a local browser to complete consent, which made it unusable on a
deployed/headless server. Added a free-tier usage warning in the UI
recommending short (1-2 minute) demo clips.

## Known Limitations

- Both transcription providers run on free-tier accounts for this demo —
  long audio files may hit rate/quota limits, so short clips (1-2 minutes)
  are recommended for trying the project out.
- The recipient email field is open text with only basic format validation;
  there's no login gate, so anyone with the link can trigger an email send
  to any address they enter.
- `temp_uploads/` and `reports/` are cleared/created at runtime and are not
  intended for long-term storage of audio files or reports.
- Action items with 🟡 low confidence are best-effort inferences and should
  be reviewed by a human before being pushed into downstream tools.

## Roadmap

- Direct integrations with Notion, Jira, and GitHub for auto-creating action
  items (currently only email delivery is implemented).
- Support for live meeting recording, not just pre-recorded file upload.
- Multi-recipient / configurable distribution lists for report delivery.