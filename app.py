# app.py
import streamlit as st
import requests

API_BASE_URL = "https://docbot-7eol.onrender.com"

st.set_page_config(page_title="DocBot - Chat with Your Documents")
st.title("📄 DocBot - Ask Questions from Your PDF")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("📤 Uploading..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        try:
            upload_resp = requests.post(f"{API_BASE_URL}/upload/", files=files)
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
            st.stop()

    if upload_resp.status_code == 200:
        data = upload_resp.json()
        doc_id = data["doc_id"]
        filename = data["filename"]
        st.success("✅ Uploaded!")

        with st.spinner("🛠️ Processing..."):
            process_resp = requests.post(f"{API_BASE_URL}/process/", json={"doc_id": doc_id})
        if process_resp.status_code == 200:
            st.success("✅ Processing complete!")
        else:
            st.error("❌ Processing failed.")
    else:
        st.error("❌ Upload failed.")
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
            st.markdown(f"### 🧠 Answer:\n{result['answer']}")
            if result.get("sources"):
                st.markdown("#### 📚 Sources:")
                for src in result["sources"]:
                    page = src.get("page")
                    para = src.get("paragraph")
                    file = src.get("doc_id")
                    url = f"{API_BASE_URL}/files/{file}"
                    st.markdown(f"- [Page {page}, Paragraph {para}]({url})")
        else:
            st.error("❌ Could not get a response.")
else:
    st.info("📎 Upload a PDF to begin.")
