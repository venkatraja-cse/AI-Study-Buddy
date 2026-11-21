import json
import os
from io import BytesIO

import streamlit as st
from pypdf import PdfReader
from google import genai

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="centered"
)

st.title("📚 AI Study Buddy")
st.write("Turn your study notes into a quick revision pack using Gemini AI.")

# -------------------- API KEY --------------------
def get_api_key():
    """Read the Gemini key from Streamlit Secrets or an environment variable."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""

    return key or os.getenv("GEMINI_API_KEY", "")


# -------------------- PDF TEXT EXTRACTION --------------------
def extract_pdf_text(uploaded_file):
    """Extract selectable text from an uploaded PDF."""
    pdf_bytes = BytesIO(uploaded_file.getvalue())
    reader = PdfReader(pdf_bytes)

    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


# -------------------- GEMINI REQUEST --------------------
def create_revision_pack(notes, api_key):
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a helpful study assistant. Use ONLY the study notes provided below.
Do not invent facts that are not supported by the notes. If something is missing,
say that it is not mentioned in the notes.

Return ONLY valid JSON with this exact structure:
{{
  "summary": ["5 to 6 concise bullet points"],
  "questions": [
    {{
      "question": "A multiple-choice question",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "A. ...",
      "explanation": "A short explanation based on the notes"
    }}
  ],
  "key_terms": [
    {{
      "term": "A key term from the notes",
      "meaning": "A simple meaning based on the notes"
    }}
  ]
}}

Requirements:
- Give 5 summary bullet points (up to 6 if needed).
- Give exactly 5 multiple-choice questions.
- Each question must have 4 options.
- Give the correct answer and a short explanation for each question.
- Give exactly 3 key terms with simple meanings.
- Make the language easy for a student to understand.
- Output valid JSON only. Do not use Markdown code fences.

STUDY NOTES:
{notes}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    response_text = (response.text or "").strip()
    # Tolerate a model response wrapped in Markdown fences.
    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "", 1)
        response_text = response_text.replace("```", "").strip()

    return json.loads(response_text)


# -------------------- INPUT --------------------
st.subheader("1. Add your study material")

uploaded_file = st.file_uploader(
    "Upload your notes as a PDF",
    type=["pdf"]
)

pasted_notes = st.text_area(
    "Or paste your study notes here",
    height=180,
    placeholder="Paste your chapter notes or study material here..."
)

if uploaded_file and pasted_notes.strip():
    st.info("Both a PDF and pasted notes were provided. The app will use the pasted notes.")
    notes = pasted_notes.strip()
elif uploaded_file:
    try:
        notes = extract_pdf_text(uploaded_file)
        if not notes:
            st.warning(
                "No selectable text was found in this PDF. "
                "If it is a scanned image PDF, paste the text into the box instead."
            )
    except Exception as exc:
        notes = ""
        st.error(f"Could not read this PDF: {exc}")
else:
    notes = pasted_notes.strip()

st.caption("Tip: For best results, use a text-based PDF or paste clear notes.")

# -------------------- GENERATE --------------------
if st.button("✨ Generate Study Materials", type="primary", use_container_width=True):
    api_key = get_api_key()

    if not api_key:
        st.error(
            "Gemini API key is not configured. Add GEMINI_API_KEY in "
            "Streamlit Cloud → App → Settings → Secrets."
        )
    elif not notes:
        st.warning("Please upload a PDF or paste your study notes first.")
    else:
        # Keep the request within a reasonable size for a student project.
        notes_for_ai = notes[:30000]

        with st.spinner("Gemini is preparing your revision pack..."):
            try:
                result = create_revision_pack(notes_for_ai, api_key)
                st.session_state["revision_pack"] = result
                st.session_state["source_notes"] = notes_for_ai
                st.success("Your study materials are ready!")
            except json.JSONDecodeError:
                st.error(
                    "Gemini returned a response that could not be read. "
                    "Please click Generate Study Materials again."
                )
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")


# -------------------- DISPLAY OUTPUT --------------------
if "revision_pack" in st.session_state:
    result = st.session_state["revision_pack"]

    st.divider()
    st.header("2. Your AI Revision Pack")

    st.subheader("📝 Summary")
    for point in result.get("summary", []):
        st.markdown(f"- {point}")

    st.subheader("❓ Practice Questions (MCQs)")
    for index, item in enumerate(result.get("questions", []), start=1):
        st.markdown(f"**{index}. {item.get('question', 'Question')}**")
        for option in item.get("options", []):
            st.write(option)

        with st.expander(f"Show answer for Question {index}"):
            st.success(f"Correct answer: {item.get('answer', 'Not provided')}")
            explanation = item.get("explanation", "")
            if explanation:
                st.write(explanation)

    st.subheader("📖 Important Key Terms")
    for item in result.get("key_terms", []):
        st.markdown(f"**{item.get('term', 'Term')}**")
        st.write(item.get("meaning", ""))

    # Build a downloadable text revision pack.
    lines = ["AI STUDY BUDDY - REVISION PACK", "", "SUMMARY"]
    lines.extend([f"- {point}" for point in result.get("summary", [])])

    lines.extend(["", "PRACTICE QUESTIONS"])
    for index, item in enumerate(result.get("questions", []), start=1):
        lines.append(f"{index}. {item.get('question', '')}")
        lines.extend(item.get("options", []))
        lines.append(f"Answer: {item.get('answer', '')}")
        lines.append(f"Explanation: {item.get('explanation', '')}")
        lines.append("")

    lines.append("IMPORTANT KEY TERMS")
    for item in result.get("key_terms", []):
        lines.append(f"{item.get('term', '')}: {item.get('meaning', '')}")

    revision_text = "\n".join(lines)

    st.download_button(
        label="⬇️ Download Revision Pack",
        data=revision_text,
        file_name="AI_Study_Buddy_Revision_Pack.txt",
        mime="text/plain",
        use_container_width=True
    )

st.divider()
st.caption("Created by VENKAT RAJA S | 2026BTAI462")
