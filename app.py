import streamlit as st
import requests

# ✅ FastAPI backend base URL (without /docs)
API_BASE_URL = "https://docbot-7eol.onrender.com"

st.set_page_config(page_title="DocBot - Chat with Your Documents")
st.title("📄 DocBot - Ask Questions from Your PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    st.write(f"Uploaded: {uploaded_file.name}, {uploaded_file.size / 1024:.1f} KB")

    with st.spinner("📤 Uploading..."):
        try:
            file_bytes = uploaded_file.getvalue()
            files = {"file": (uploaded_file.name, file_bytes, "application/pdf")}
            upload_resp = requests.post(f"{API_BASE_URL}/upload/", files=files)
        except Exception as e:
            st.error(f"❌ Upload request error: {e}")
            st.stop()

    if upload_resp.status_code == 200:
        st.success("✅ File uploaded successfully!")
        doc_id = upload_resp.json().get("doc_id")
        filename = upload_resp.json().get("filename")
    else:
        st.error(f"❌ Upload failed. Status code: {upload_resp.status_code}")
        st.stop()

    # Ask question
    question = st.text_input("🤖 Ask a question from this document:")

    if st.button("Get Answer") and question.strip():
        with st.spinner("💬 Thinking..."):
            query_data = {"question": question, "doc_id": doc_id}
            try:
                response = requests.post(f"{API_BASE_URL}/query/", json=query_data)
            except Exception as e:
                st.error(f"❌ Query failed: {e}")
                st.stop()

        if response.status_code == 200:
            result = response.json()
            st.markdown("### 🧠 Answer")
            st.markdown(result["summary"])

            if result.get("answers"):
                st.markdown("#### 📚 Sources")
                for src in result["answers"]:
                    citation = src["citation"]
                    page = citation.get("page", "?")
                    para = citation.get("paragraph", "?")
                    file_url = f"{API_BASE_URL}/files/{filename}"
                    st.markdown(f"- [Page {page}, Paragraph {para}]({file_url})")
        else:
            st.error("❌ Could not get a response.")
else:
    st.info("📌 Upload a PDF to begin.")
