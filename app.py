
import streamlit as st
from google import genai
from pypdf import PdfReader
import os

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="centered"
)

st.title("📚 AI Study Buddy")
st.write("Convert your notes into summaries, quizzes and revision materials!")

# Get Gemini API key securely
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

if not api_key:
    st.error("Gemini API key is not configured. Add it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

st.subheader("📄 Upload your notes")

uploaded_file = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"]
)

pasted_notes = st.text_area(
    "Or paste your notes here",
    height=180,
    placeholder="Paste your study notes..."
)

def extract_pdf(file):
    reader = PdfReader(file)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)

if st.button("✨ Generate Study Material", type="primary"):

    notes = pasted_notes.strip()

    if uploaded_file is not None:
        try:
            notes = extract_pdf(uploaded_file).strip()
        except Exception as e:
            st.error(f"Could not read PDF: {e}")
            st.stop()

    if not notes:
        st.warning("Please upload a PDF or paste your notes.")
        st.stop()

    with st.spinner("AI is preparing your study materials..."):

        prompt = f"""
You are an AI Study Buddy.

Read the following study notes and create:

1. SUMMARY:
Give exactly 5 to 6 important bullet points.

2. MULTIPLE CHOICE QUESTIONS:
Create exactly 5 MCQs.
Each question must have 4 options (A, B, C, D).
Give the correct answer after each question.

3. IMPORTANT TERMS:
Explain exactly 3 important terms in simple English.

4. REVISION TIPS:
Give a short list of important points to revise.

Use clear, student-friendly English.
Only use information supported by the notes.
If information is missing, do not invent it.

STUDY NOTES:
{notes}
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text or "No response generated."

            st.session_state["study_result"] = result

        except Exception as e:
            st.error(f"AI generation failed: {e}")

if "study_result" in st.session_state:

    st.divider()
    st.subheader("🎓 Your Study Materials")

    st.markdown(st.session_state["study_result"])

    st.download_button(
        label="⬇️ Download Revision Pack",
        data=st.session_state["study_result"],
        file_name="AI_Study_Buddy_Revision_Pack.txt",
        mime="text/plain"
    )

st.divider()
st.caption("Created by VENKAT RAJA S | 2026BTAI462 | JOY UNIVERSITY")
   
