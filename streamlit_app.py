import streamlit as st
import requests

API_BASE_URL = "https://docbot-7eol.onrender.com"

st.set_page_config(page_title="📄 DocBot", layout="centered")
st.title("📄 DocBot – Chat with your PDFs")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
st.write(f"Uploaded: {uploaded_file.name}, {uploaded_file.size / 1024:.1f} KB")

python
Copy
Edit
with st.spinner("📤 Uploading..."):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        upload_resp = requests.post(f"{API_BASE_URL}/upload/", files=files)
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
        st.stop()

if upload_resp.status_code == 200:
    st.success("✅ File uploaded successfully!")
    data = upload_resp.json()
    doc_id = data.get("doc_id")

    question = st.text_input("🤖 Ask a question from this document:")

    if st.button("Get Answer") and question.strip():
        with st.spinner("💬 Thinking..."):
            query_payload = {"question": question, "doc_id": doc_id}
            try:
                response = requests.post(f"{API_BASE_URL}/query/", json=query_payload)
            except Exception as e:
                st.error(f"❌ Query failed: {e}")
                st.stop()

        if response.status_code == 200:
            result = response.json()
            st.markdown("### 🧠 Answer:")
            st.write(result.get("summary"))

            if result.get("answers"):
                st.markdown("#### 📚 Sources:")
                for ans in result["answers"]:
                    meta = ans["citation"]
                    page = meta.get("page")
                    para = meta.get("paragraph")
                    doc = meta.get("doc_id")
                    link = f"{API_BASE_URL}/files/{doc}"
                    st.markdown(f"- [Page {page}, Paragraph {para}]({link})")
        else:
            st.error("❌ Could not get an answer.")
else:
    st.error("❌ Upload failed. Please try again.")
else:
st.info("📎 Upload a PDF to get started.")
