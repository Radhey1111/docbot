import streamlit as st
import requests

# ✅ Your FastAPI backend URL on Render
FASTAPI_URL = "https://docbot-7eol.onrender.com"

st.set_page_config(page_title="DocBot - Chat with Your Documents", layout="centered")
st.title("📄 DocBot - Ask Questions from Your PDF")

# File upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("📤 Uploading and processing..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{FASTAPI_URL}/upload/", files=files)

    if response.status_code == 200:
        st.success("✅ File uploaded successfully!")
        data = response.json()
        doc_id = data.get("doc_id", "")
        filename = data.get("filename", "")
    else:
        st.error("❌ Upload failed. Please try again.")
        st.stop()
else:
    st.info("📎 Upload a PDF file to get started.")
    st.stop()

# Ask question
question = st.text_input("🤖 Ask a question about the uploaded document:")

if st.button("Get Answer") and question.strip() != "":
    with st.spinner("💬 Generating answer..."):
        query_data = {"question": question, "doc_id": doc_id}
        response = requests.post(f"{FASTAPI_URL}/query/", json=query_data)

    if response.status_code == 200:
        result = response.json()
        st.markdown(f"### 🧠 Answer:\n{result['answer']}")

        # 📎 Show citations if available
        if result.get("sources"):
            st.markdown("#### 📚 Sources:")
            for src in result["sources"]:
                page = src.get("page")
                para = src.get("paragraph")
                file = src.get("doc_id")
                url = f"{FASTAPI_URL}/files/{file}"
                st.markdown(f"- [Page {page}, Paragraph {para}]({url})")
    else:
        st.error("❌ Failed to get a response. Please try again.")
