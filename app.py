
import streamlit as st
from pypdf import PdfReader
import re
from collections import Counter

st.set_page_config(page_title="AI Study Buddy", page_icon="📚")

st.title("📚 AI Study Buddy")
st.write("Turn your notes into revision materials!")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

pasted_notes = st.text_area(
    "Or paste your study notes",
    height=180
)

def extract_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def make_summary(notes):
    sentences = re.split(r'(?<=[.!?])\s+', notes)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    return sentences[:6]

def make_terms(notes):
    words = re.findall(r'\b[A-Za-z]{5,}\b', notes.lower())
    common = Counter(words).most_common(3)
    return [word for word, count in common]

if st.button("Generate Study Materials"):
    notes = pasted_notes.strip()

    if uploaded_file:
        notes = extract_pdf(uploaded_file).strip()

    if not notes:
        st.warning("Please upload a PDF or paste notes.")
    else:
        summary = make_summary(notes)
        terms = make_terms(notes)

        st.session_state["summary"] = summary
        st.session_state["terms"] = terms
        st.session_state["notes"] = notes

if "summary" in st.session_state:
    st.divider()

    st.subheader("📝 Summary")
    for point in st.session_state["summary"]:
        st.write("•", point)

    st.subheader("📖 Important Terms")
    for term in st.session_state["terms"]:
        st.write("•", term.capitalize())

    st.subheader("❓ Practice Questions")

    questions = [
        "What is the main topic of your notes?",
        "Which concept is important in the notes?",
        "What is the purpose of the topic?",
        "Which term appears in the notes?",
        "What did you learn from this topic?"
    ]

    for i, question in enumerate(questions, 1):
        st.write(f"**{i}. {question}**")

    revision = "AI STUDY BUDDY - REVISION PACK\n\n"
    revision += "SUMMARY\n"
    revision += "\n".join("- " + x for x in st.session_state["summary"])
    revision += "\n\nIMPORTANT TERMS\n"
    revision += "\n".join(st.session_state["terms"])
    revision += "\n\nPRACTICE QUESTIONS\n"
    revision += "\n".join(questions)

    st.download_button(
        "⬇️ Download Revision Pack",
        data=revision,
        file_name="Revision_Pack.txt",
        mime="text/plain"
    )

st.divider()
st.caption("Created by VENKAT RAJA S | 2026BTAI462")
st.caption("Demo Mode – Uses basic text extraction, not Gemini AI.")
    
