from fastapi import FastAPI, UploadFile, File
import shutil
from pypdf import PdfReader

app = FastAPI()


# Function for chunking text
def chunk_text(text, chunk_size=50):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks


@app.get("/")
def home():
    return {"message": "Mini RAG Backend Running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Save uploaded file
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read PDF
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

    # Create chunks
    chunks = chunk_text(text)

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "first_chunk": chunks[0]
    }