import streamlit as st
import requests


API_BASE_URL = "https://chatbotthemeidentifier-s6xt.onrender.com"

st.set_page_config(page_title="📄 DocBot", layout="wide")
st.title("📄 DocBot – Chat with your PDFs")


uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
with st.spinner("📤 Uploading and processing..."):
try:
files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
response = requests.post(f"{API_BASE_URL}/upload/", files=files)
response.raise_for_status()
except Exception as e:
st.error(f"❌ Upload failed: {e}")
st.stop()

kotlin
Copy
Edit
if response.status_code == 200:
    data = response.json()
    doc_id = data.get("doc_id")
    filename = data.get("filename")
    st.success("✅ File uploaded successfully!")
else:
    st.error(f"❌ Upload failed with status code {response.status_code}")
    st.stop()

# Ask question
question = st.text_input("🤖 Ask a question about your document:")

if question and st.button("Get Answer"):
    with st.spinner("💬 Generating answer..."):
        try:
            response = requests.post(f"{API_BASE_URL}/query/", json={"question": question, "doc_id": doc_id})
            response.raise_for_status()
        except Exception as e:
            st.error(f"❌ Query failed: {e}")
            st.stop()

        data = response.json()
        st.markdown("### 🧠 Answer:")
        st.write(data.get("summary", "No summary generated."))

        if "answers" in data:
            st.markdown("### 📚 Supporting Sources:")
            for i, ans in enumerate(data["answers"]):
                citation = ans.get("citation", {})
                page = citation.get("page", "?")
                para = citation.get("paragraph", "?")
                file = citation.get("doc_id", "")
                st.markdown(f"**Answer {i+1}:** {ans['content']}")
                st.markdown(f"🔗 [Page {page}, Paragraph {para}]({API_BASE_URL}/files/{file})")
else:
st.info("📎 Upload a PDF file to begin.")
