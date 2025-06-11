import streamlit as st
import requests

# --- Streamlit Config ---
st.set_page_config(page_title="📄 DocBot: Document QA Chatbot", layout="wide")
st.title("📄 DocBot: Document QA Chatbot")

# --- Theme Toggle ---
theme = st.sidebar.radio("🎨 Choose Theme", ["Light", "Dark"], index=0)

def apply_custom_theme(theme):
    if theme == "Dark":
        dark_css = """
        <style>
            body, .stApp {
                background-color: #1e1e1e !important;
                color: #ffffff !important;
            }
            .stTextInput input, .stTextArea textarea, .stButton button {
                background-color: #333 !important;
                color: #fff !important;
                border: 1px solid #555 !important;
            }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)
    else:
        light_css = """
        <style>
            body, .stApp {
                background-color: #ffffff !important;
                color: #000000 !important;
            }
            .stTextInput input, .stTextArea textarea, .stButton button {
                background-color: #fff !important;
                color: #000 !important;
                border: 1px solid #ccc !important;
            }
        </style>
        """
        st.markdown(light_css, unsafe_allow_html=True)

apply_custom_theme(theme)

# --- State Initialization ---
if 'doc_id' not in st.session_state:
    st.session_state.doc_id = None
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []  # stores list of (question, summary, answers)

# --- Upload Section ---
st.sidebar.header("Upload Document")
uploaded_file = st.sidebar.file_uploader(
    "Choose a file (PDF, TXT, or Image)",
    type=["pdf", "txt", "jpg", "jpeg", "png"]
)

if uploaded_file:
    with st.spinner("Uploading and processing..."):
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        res = requests.post("http://localhost:8000/upload/", files=files)
        if res.status_code == 200:
            data = res.json()
            st.sidebar.success("✅ File uploaded successfully")
            st.session_state.doc_id = data.get("doc_id")
            st.session_state.filename = data.get("filename")
            st.session_state.qa_history = []  # Reset history on new upload
        else:
            st.sidebar.error(f"❌ Upload failed: {res.status_code} - {res.text}")

# --- Question Section ---
st.subheader("Ask a Question")
question = st.text_input("Enter your question")

if st.button("Get Answer"):
    if not st.session_state.get("doc_id"):
        st.warning("⚠️ Please upload a document first.")
    elif question.strip() == "":
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("Searching..."):
            res = requests.post("http://localhost:8000/query/", json={
                "question": question,
                "doc_id": st.session_state.doc_id
            })

            if res.status_code == 200:
                data = res.json()
                summary = data["summary"]
                answers = data["answers"]

                # Save to history
                st.session_state.qa_history.append({
                    "question": question,
                    "summary": summary,
                    "answers": answers
                })
            else:
                st.error(f"❌ Query failed: {res.status_code} - {res.text}")

# --- Display Question History ---
if st.session_state.qa_history:
    st.markdown("## 🗃️ Question History")

    # --- Clear History Button ---
    if st.button("🧹 Clear Question History"):
        st.session_state.qa_history = []
        st.experimental_rerun()

    for i, entry in enumerate(reversed(st.session_state.qa_history), 1):
        st.markdown(f"### ❓ Question {len(st.session_state.qa_history)-i+1}: {entry['question']}")

        st.markdown("#### 🧠 Summary")
        st.markdown(
            f"<div style='background-color: #f9f9f9; padding: 10px; border-left: 5px solid #4CAF50;'>"
            f"{entry['summary']}</div>",
            unsafe_allow_html=True
        )

        st.markdown("#### 🔍 Answers")
        for j, item in enumerate(entry["answers"]):
            citation = item["citation"]
            page = citation.get("page")
            para = citation.get("paragraph")
            doc_id = citation.get("doc_id")
            filename = st.session_state.get("filename", "")

            if filename and isinstance(page, int):
                link = f"http://localhost:8000/files/{filename}#page={page}"
                citation_str = f"<a href='{link}' target='_blank'>📚 Page {page}, Para {para} (Doc ID: {doc_id})</a>"
            else:
                citation_str = f"📚 Page {page}, Para {para} (Doc ID: {doc_id})"

            st.markdown(f"""
            <div style='margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;'>
                <b>Answer {j+1}:</b><br>
                {item['content']}<br>
                <span style='color: #4CAF50; font-size: 0.9em;'>
                    {citation_str}
                </span>
            </div>
            """, unsafe_allow_html=True)
