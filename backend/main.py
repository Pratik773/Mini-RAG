from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
print("API KEY =", os.getenv("GROQ_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(name="documents")


# Request model
class QueryRequest(BaseModel):
    question: str


# Chunking function
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

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):

        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[f"{file.filename}_{index}"],
            embeddings=[embedding],
            documents=[chunk]
        )

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "message": "Embeddings stored successfully"
    }


@app.post("/ask")
async def ask_question(request: QueryRequest):

    question = request.question

    # Convert question into embedding
    query_embedding = model.encode(question).tolist()

    # Retrieve similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    retrieved_chunks = results["documents"][0]

    context = "\n".join(retrieved_chunks)

    # Prompt for LLM
    prompt = f"""
    Answer the question only using the context below.

    Context:
    {context}

    Question:
    {question}
    """

    try:

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = completion.choices[0].message.content

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks
        }

    except Exception as e:
        print(e)
        # Fallback mode
        return {
            "question": question,
            "fallback_mode": True,
            "message": "LLM unavailable. Returning retrieved chunks only.",
            "retrieved_chunks": retrieved_chunks
        }