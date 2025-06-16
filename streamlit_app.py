import streamlit as st
import requests

API_BASE_URL = "https://chatbotthemeidentifier-s6xt.onrender.com"

st.set_page_config(page_title="DocBot – Chat with your PDFs", layout="centered")
st.title("📄 DocBot – Chat with your PDFs")

uploaded_file = st.file_uploader("📎 Upload a PDF file", type=["pdf"])

if uploaded_file:
with st.spinner("📤 Uploading and processing..."):
try:
files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
response = requests.post(f"{API_BASE_URL}/upload/", files=files)
response.raise_for_status()
except Exception as e:
st.error(f"❌ Upload failed: {e}")
st.stop()

python
Copy
Edit
data = response.json()
doc_id = data.get("doc_id")
filename = data.get("filename")

st.success("✅ File uploaded successfully!")

question = st.text_input("💬 Ask a question about the uploaded document:")

if st.button("Get Answer") and question.strip():
    with st.spinner("🔎 Searching for answer..."):
        try:
            query_data = {"question": question, "doc_id": doc_id}
            response = requests.post(f"{API_BASE_URL}/query/", json=query_data)
            response.raise_for_status()
        except Exception as e:
            st.error(f"❌ Query failed: {e}")
            st.stop()

    result = response.json()
    summary = result.get("summary", "")
    answers = result.get("answers", [])

    st.markdown(f"### 🧠 Summary:\n{summary}")

    if answers:
        st.markdown("#### 📚 References:")
        for i, ans in enumerate(answers, 1):
            citation = ans["citation"]
            content = ans["content"]
            st.markdown(f"{i}. {content}\n\nSource: Page {citation.get('page')}, Para {citation.get('paragraph')}")
else:
st.info("📄 Please upload a PDF to get started.")
