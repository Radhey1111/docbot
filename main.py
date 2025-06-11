from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pdfplumber
import pytesseract
from PIL import Image
import os
import shutil
import uuid
from dotenv import load_dotenv
from vector_store import create_vector_store, load_vector_store
from huggingface_hub import InferenceClient

# Load env variables
load_dotenv()

# --- Init FastAPI ---
app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Directories ---
UPLOAD_DIR = "uploaded_docs"
TEXT_DIR = "extracted_texts"
SUMMARY_DIR = "summaries"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

# --- Serve uploaded PDFs ---
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# --- Text Extraction ---
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

# --- Upload Endpoint ---
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split('.')[-1]
    uid = str(uuid.uuid4())
    saved_filename = f"{uid}_{file.filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    if file_ext.lower() == "pdf":
        extracted_text = extract_text_from_pdf(saved_path)
    elif file_ext.lower() in ["jpg", "jpeg", "png"]:
        extracted_text = extract_text_from_image(saved_path)
    else:
        content = await file.read()
        extracted_text = content.decode("utf-8")

    # Save raw text
    with open(os.path.join(TEXT_DIR, f"{uid}.txt"), "w") as f:
        f.write(extracted_text)

    # Prepare chunks
    paragraphs = extracted_text.split('\n')
    texts = [p.strip() for p in paragraphs if len(p.strip()) > 20]
    print("📄 Prepared chunks:", texts)

    # Create vector store with metadata
    create_vector_store(texts, uid)

    # Create empty summary file
    with open(os.path.join(SUMMARY_DIR, f"{uid}.txt"), "w") as sf:
        sf.write(f"Summary not generated yet for {uid}")

    return {
        "message": "✅ File uploaded and vector store created",
        "doc_id": uid,
        "filename": saved_filename
    }

# --- Query Endpoint ---
@app.post("/query/")
async def query_answer(request: Request):
    body = await request.json()
    question = body.get("question", "")
    doc_id = body.get("doc_id", "")

    db = load_vector_store()
    results = db.similarity_search_with_score(question, k=5)

    answers = []
    for doc, score in results:
        metadata = doc.metadata or {}
        citation = {
            "page": metadata.get("page", "?"),
            "paragraph": metadata.get("paragraph", "?"),
            "doc_id": metadata.get("doc_id", "?")
        }
        answers.append({
            "content": doc.page_content,
            "score": score,
            "citation": citation
        })

    synthesized_answer = synthesize_theme(question, answers)

    # Save summary
    if answers:
        summary_path = os.path.join(SUMMARY_DIR, f"{answers[0]['citation']['doc_id']}.txt")
        with open(summary_path, "w") as f:
            f.write(synthesized_answer)

    return {
        "answers": answers,
        "summary": synthesized_answer
    }

# --- Theme Synthesis with Falcon ---
import traceback
from huggingface_hub import InferenceClient

# Initialize Hugging Face Inference Client
cclient = InferenceClient(
    model="google/flan-t5-large",
    token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)


def synthesize_theme(question, answers):
    # Combine answers into a formatted context for the prompt
    combined_content = "\n\n".join(
        [f"Doc {i+1}: {a['content']} (Source: Page {a['citation']['page']}, Para {a['citation']['paragraph']})"
         for i, a in enumerate(answers)]
    )

    prompt = f"""You are an expert assistant helping analyze answers from documents.

Question: {question}

Extracted Answers:
{combined_content}

Instructions:
- Identify 1–2 key themes across the above answers.
- Summarize each theme in a few lines.
- Provide the citations (e.g., Page X Para Y) that support each theme.

Return the output in this format:
Theme 1 - [Title]:
Summary...
Sources: Page X Para Y, Page A Para B

Theme 2 - [Title]:
Summary...
Sources: ...
"""

    try:
        print("🧠 Sending prompt to Falcon...")
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=400,  # Falcon sometimes fails >512
            temperature=0.3,
            stop_sequences=["\n\n"]
        )
        print("✅ Falcon response received.")
        return response.strip()
    
    except Exception as e:
        print("❌ Error in Falcon synthesis:")
        traceback.print_exc()
        return f"Theme synthesis failed. Error: {str(e)}"
