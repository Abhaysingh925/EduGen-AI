from fastapi.openapi.utils import get_openapi
from io import BytesIO
from uuid import uuid4
from hashlib import sha256
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from document_pipeline import process_document
from retrieval import search_chunks
from llm import explain_topic


app = FastAPI(
    title="EduGen-AI API",
    description="Backend API for EduGen-AI Academic Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory session storage
sessions = {}

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx"}


class NamedBytesIO(BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


class AskRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1, max_length=2000)
    language: str = "English"
    level: str = "College beginner"
    category: str = "All"
    subject: str = "All"
    chapter: str = "All"
    top_k: int = Field(default=6, ge=3, le=10)


@app.get("/")
def home():
    return {
        "message": "Welcome to EduGen-AI Backend",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "application": "EduGen-AI",
        "backend": "FastAPI"
    }


@app.post("/api/session")
def create_session():
    session_id = str(uuid4())

    sessions[session_id] = {
        "chunks": [],
        "documents": [],
        "file_hashes": set()
    }

    return {
        "session_id": session_id,
        "message": "Session created successfully"
    }


@app.post("/api/upload")
async def upload_documents(
    session_id: str = Form(...),
    files: list[UploadFile] = File(...),
    subject: str = Form("Unassigned"),
    chapter: str = Form("Unassigned"),
    chunk_size: int = Form(900),
    overlap: int = Form(120)
):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if not files or len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Upload between 1 and 10 files."
        )

    if chunk_size not in [500, 700, 900, 1200, 1500]:
        raise HTTPException(status_code=400, detail="Invalid chunk size.")

    if overlap not in [0, 50, 100, 120, 150, 200]:
        raise HTTPException(status_code=400, detail="Invalid overlap.")

    session = sessions[session_id]
    uploaded = []
    errors = []
    skipped = 0

    for file in files:
        filename = Path(file.filename or "").name
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            errors.append({
                "filename": filename,
                "error": "Only PDF, DOCX and PPTX are supported."
            })
            continue

        try:
            content = await file.read()

            if not content:
                errors.append({
                    "filename": filename,
                    "error": "File is empty."
                })
                continue

            if len(content) > MAX_FILE_SIZE:
                errors.append({
                    "filename": filename,
                    "error": "File exceeds the 10 MB limit."
                })
                continue

            digest = sha256(content).hexdigest()

            if digest in session["file_hashes"]:
                skipped += 1
                continue

            document_file = NamedBytesIO(content, filename)

            chunks = process_document(
                document_file,
                chunk_size=chunk_size,
                overlap=overlap
            )

            if not chunks:
                errors.append({
                    "filename": filename,
                    "error": "No extractable text found."
                })
                continue

            subject_value = subject.strip() or "Unassigned"
            chapter_value = chapter.strip() or "Unassigned"

            for chunk in chunks:
                chunk["subject"] = subject_value
                chunk["chapter"] = chapter_value

            session["chunks"].extend(chunks)
            session["file_hashes"].add(digest)

            document_info = {
                "name": filename,
                "format": extension.lstrip(".").upper(),
                "subject": subject_value,
                "chapter": chapter_value,
                "category": chunks[0].get("category", "Other"),
                "chunks": len(chunks),
                "size_kb": round(len(content) / 1024, 1)
            }

            session["documents"].append(document_info)
            uploaded.append(document_info)

        except Exception as exc:
            errors.append({
                "filename": filename,
                "error": f"Processing failed: {type(exc).__name__}"
            })

        finally:
            await file.close()

    return {
        "message": "Upload processing completed",
        "uploaded": uploaded,
        "skipped_duplicates": skipped,
        "errors": errors,
        "total_documents": len(session["documents"]),
        "total_chunks": len(session["chunks"])
    }


@app.post("/api/ask")
def ask_question(request: AskRequest):
    session = sessions.get(request.session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    results = search_chunks(
        session["chunks"],
        request.question,
        top_k=request.top_k,
        category=request.category,
        subject=request.subject,
        chapter=request.chapter
    )

    if not results:
        return {
            "answer": "No matching passages found. Try another question or upload relevant study material.",
            "mode": "No matching sources",
            "notice": "",
            "sources": []
        }

    generation = explain_topic(
        question=request.question,
        results=results,
        language=request.language,
        level=request.level
    )

    sources = [
        {
            "source": item.get("source", "Unknown"),
            "category": item.get("category", "Other"),
            "page": item.get("page", "?"),
            "location_type": item.get("location_type", "page"),
            "score": item.get("score"),
            "text": item.get("text", "")
        }
        for item in results
    ]

    return {
        "answer": generation["answer"],
        "mode": generation["mode"],
        "notice": generation["notice"],
        "sources": sources
    }


@app.get("/api/session/{session_id}/summary")
def session_summary(session_id: str):
    session = sessions.get(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "documents": session["documents"],
        "total_documents": len(session["documents"]),
        "total_chunks": len(session["chunks"])
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["openapi"] = "3.0.3"
    
    upload_schema = schema["components"]["schemas"].get(
        "Body_upload_documents_api_upload_post"
    )

    if upload_schema:
        upload_schema["properties"]["files"] = {
            "type": "array",
            "title": "Files",
            "items": {
                "type": "string",
                "format": "binary"
            }
        }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
