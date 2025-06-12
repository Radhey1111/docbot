import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from uuid import uuid4

# Load remote inference API embeddings (to avoid memory issues)
embedding_model = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.environ["HUGGINGFACEHUB_API_TOKEN"],
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Set the persistent directory for Chroma
CHROMA_DIR = "chroma_db"

def create_vector_store(texts: list, doc_id: str):
    """
    Create or update a Chroma vector store from a list of texts (with or without metadata).
    """

    # Check if plain strings or dicts
    if isinstance(texts[0], str):
        documents = [
            Document(page_content=chunk, metadata={"doc_id": doc_id})
            for chunk in texts
        ]
    else:
        documents = [
            Document(page_content=chunk["content"], metadata=chunk["metadata"])
            for chunk in texts
        ]

    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )
    db.persist()
    return db


def load_vector_store():
    """
    Load the existing Chroma vector store from disk.
    """
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

def query_vector_store(query: str, k: int = 5):
    """
    Query the Chroma store for top-k matches to the input query.
    """
    db = load_vector_store()
    results = db.similarity_search_with_score(query, k=k)
    return results
