import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# --- Constants ---
CHROMA_DIR = "vectorstore"

# --- HuggingFace Embeddings ---
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- Text Splitter ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# === Create Vector Store ===
def create_vector_store(texts, uid="unknown"):
    print("🛠 Creating vector store for doc_id:", uid)
    documents = []

    for para_num, text in enumerate(texts):
        if not text.strip():
            continue
        for chunk in text_splitter.split_text(text):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "page": para_num // 5 + 1,      # Approx page number
                    "paragraph": para_num,
                    "doc_id": uid
                }
            ))

    db = Chroma.from_documents(
        documents,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )
    db.persist()
    print("✅ Vector store created and persisted.")

# === Load Vector Store ===
def load_vector_store():
    print("📦 Loading Chroma vector store from:", CHROMA_DIR)
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

# === Optional: Initialize Vector Store ===
def init_vector_store(pages, uid="unknown"):
    if os.path.exists(CHROMA_DIR) and os.path.exists(os.path.join(CHROMA_DIR, "chroma-collections.parquet")):
        print("🔁 Vector store found. Loading...")
        return load_vector_store()
    else:
        print("🆕 No vector store found. Creating a new one...")
        create_vector_store(pages, uid)
        return load_vector_store()

# === Query Vector Store ===
def query_vector_store(query, vector_store):
    print("🔎 Querying vector store...")
    results = vector_store.similarity_search_with_score(query, k=5)
    formatted = []

    for doc, score in results:
        metadata = doc.metadata or {}
        formatted.append({
            "content": doc.page_content,
            "score": score,
            "citation": {
                "page": metadata.get("page", "?"),
                "paragraph": metadata.get("paragraph", "?"),
                "doc_id": metadata.get("doc_id", "?")
            }
        })
    return formatted
