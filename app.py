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

from pipeline import process_meeting

st.set_page_config(page_title="Meeting Assistant", layout="wide")

st.title("🎙️ Urdu-English Meeting Assistant")
st.write("Upload a meeting recording to get a transcript, summary, and action items.")

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

        progress_placeholder.info("🎙️ Transcribing audio...")
        result = process_meeting(temp_path)
        progress_placeholder.empty()

        if result["success"]:
            st.session_state["result"] = result
            st.success("Meeting processed successfully!")
        else:
            st.error(f"Something went wrong at the {result['stage_failed']} stage: {result['error']}")
        
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