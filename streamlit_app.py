import streamlit as st
import requests

API_BASE_URL = "https://chatbotthemeidentifier-s6xt.onrender.com"

st.set_page_config(page_title="📄 DocBot", layout="wide")
st.title("📄 DocBot – Ask Questions from Your PDF")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
st.write(f"Uploaded: {uploaded_file.name}, {uploaded_file.size / 1024:.1f} KB")

python
Copy
Edit
with st.spinner("📤 Uploading..."):
    try:
        file_bytes = uploaded_file.getvalue()
        files = {"file": (uploaded_file.name, file_bytes, "application/pdf")}
        res = requests.post(f"{API_BASE_URL}/upload/", files=files)
    except Exception as e:
        st.error(f"❌ Upload error: {e}")
        st.stop()

if res.status_code == 200:
    st.success("✅ File uploaded!")
    doc_id = res.json().get("doc_id")
    question = st.text_input("Ask a question about your document:")

    if st.button("Get Answer") and question.strip():
        with st.spinner("💬 Thinking..."):
            try:
                res2 = requests.post(f"{API_BASE_URL}/query/", json={"question": question, "doc_id": doc_id})
            except Exception as e:
                st.error(f"❌ Query error: {e}")
                st.stop()

            if res2.status_code == 200:
                result = res2.json()
                st.markdown("### 🧠 Answer:")
                st.write(result.get("summary", "No answer found."))

                st.markdown("### 📚 Sources:")
                for i, src in enumerate(result.get("answers", [])):
                    meta = src["citation"]
                    st.markdown(f"- Page {meta.get('page')}, Para {meta.get('paragraph')} (Doc ID: {meta.get('doc_id')})")
            else:
                st.error("❌ Failed to retrieve answer.")
else:
    st.error("❌ Upload failed.")
else:
st.info("📎 Upload a PDF to begin.")
