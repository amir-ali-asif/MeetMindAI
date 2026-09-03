import streamlit as st
import os
import sys
import glob

# Clean up old temp files older than current session (simple approach for MVP)
if "cleaned_temp" not in st.session_state:
    for f in glob.glob("temp_uploads/*"):
        try:
            os.remove(f)
        except:
            pass
    st.session_state["cleaned_temp"] = True

# Allow importing from the src/ folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import re
from pipeline import process_meeting, send_report_to_email

st.set_page_config(page_title="Meeting Assistant", layout="wide")

st.title("🎙️ Urdu-English Meeting Assistant")

st.subheader("Choose Transcription Model")

# Keep track of selected model in session state, default to ElevenLabs
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = "elevenlabs"

col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ ElevenLabs", use_container_width=True,
                 type="primary" if st.session_state["selected_model"] == "elevenlabs" else "secondary"):
        st.session_state["selected_model"] = "elevenlabs"

with col2:
    if st.button("🎙️ Speechmatics", use_container_width=True,
                 type="primary" if st.session_state["selected_model"] == "speechmatics" else "secondary"):
        st.session_state["selected_model"] = "speechmatics"

# Display constraint info based on selection
if st.session_state["selected_model"] == "elevenlabs":
    st.info("ElevenLabs (Free Tier)")
else:
    st.info("Speechmatics (Free Tier)")

st.divider()

st.write("Upload a meeting recording to get a transcript, summary, and action items.")

st.warning(
    "⚠️ Both transcription providers (ElevenLabs and Speechmatics) are running on "
    "free-tier limits for this demo. Please use a short audio clip (1-2 minutes) "
    "just to get a feel for how the project works, rather than a full-length meeting."
)

uploaded_file = st.file_uploader(
    "Upload your meeting audio",
    type=["wav", "mp3", "m4a", "ogg"]
)

if uploaded_file is not None:
    # Save the uploaded file temporarily so our pipeline can read it
    temp_path = os.path.join("temp_uploads", uploaded_file.name)
    os.makedirs("temp_uploads", exist_ok=True)

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Process Meeting"):
        progress_placeholder = st.empty()
        progress_placeholder.info(f"🎙️ Transcribing audio using {st.session_state['selected_model'].capitalize()}...")
        result = process_meeting(temp_path, preferred_model=st.session_state["selected_model"])
        progress_placeholder.empty()

        if result["success"]:
            st.session_state["result"] = result
            st.success("Meeting processed successfully!")
        else:
            st.error(f"Something went wrong at the {result['stage_failed']} stage: {result['error']}")

# --- Everything below is OUTSIDE the "Process Meeting" button block ---
# --- so it persists correctly across reruns (e.g. when clicking "Send Report") ---

if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()
    st.subheader("📄 Transcript")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original (Urdu Script)**")
        st.text_area("", result["display_transcript"], height=250, key="original_transcript")

    with col2:
        st.markdown("**English Translation**")
        st.text_area("", result["english_transcript"], height=250, key="english_transcript")

    st.caption(f"Transcribed using: {result['transcription_provider'].capitalize()}")

    st.divider()
    st.subheader("📝 Summary")
    st.write(result["summary"])

    st.subheader("✅ Key Decisions")
    for decision in result["key_decisions"]:
        st.markdown(f"- {decision}")

    st.divider()
    st.subheader("📋 Action Items")

    for item in result["action_items"]:
        confidence_badge = "🟢 High Confidence" if item["confidence"] == "high" else "🟡 Needs Confirmation"

        with st.container(border=True):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"**Task:** {item['task']}")
                st.markdown(f"**Owner:** {item['owner'] or 'Unknown'}")
            with col_b:
                st.markdown(f"**Deadline:**")
                st.markdown(item["deadline"] or "Not specified")
            with col_c:
                st.markdown(confidence_badge)

    st.divider()
    st.subheader("📧 Send Report")

    recipient_email = st.text_input(
        "Recipient email address",
        key="recipient_email",
        placeholder="name@example.com"
    )

    if st.button("Send Report"):
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not recipient_email or not re.match(email_pattern, recipient_email.strip()):
            st.error("Please enter a valid email address before sending.")
        else:
            with st.spinner("Generating report and sending email..."):
                report_result = send_report_to_email(result, recipient_email.strip())

            if report_result["success"]:
                st.success(f"Report sent to {recipient_email.strip()}!")
            else:
                st.error(f"Failed to send report: {report_result['error']}")