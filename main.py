# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid

app = FastAPI()
UPLOAD_DIR = "docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory map of doc_id to filename
doc_map = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to DocBot API"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    doc_map[file_id] = filename
    return {"doc_id": file_id, "filename": filename}

@app.post("/process/")
def process_file(doc_id: str):
    filename = doc_map.get(doc_id)
    if not filename:
        return {"error": "Invalid doc_id"}

    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # TODO: Add your processing here — OCR, embeddings, etc.
    # Placeholder for now
    return {"message": f"Processing complete for {filename}"}

@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(path=file_path, filename=filename, media_type='application/pdf')
