"""FastAPI entrypoint for the local RAG service and static frontend."""

import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.services.rag_service import RAGService
from app.services.settings import Settings
from app.services.vector_store_service import DocumentIngestor, VectorStoreManager

logger = logging.getLogger(__name__)
settings = Settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_ingestor() -> DocumentIngestor:
    """Return a new DocumentIngestor configured from project settings."""
    return DocumentIngestor(settings)


def get_vector_manager() -> VectorStoreManager:
    """Return a VectorStoreManager for the configured local vector store."""
    return VectorStoreManager(settings)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Return a health check payload with the current model and store path."""
    return {
        "status": "ok",
        "model": settings.llm_model,
        "vector_store": str(settings.persist_directory),
    }


@app.post("/api/ingest")
async def ingest(
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> dict[str, object]:
    """Ingest either raw text or an uploaded file into the Chroma vector store."""
    try:
        if file is not None:
            contents = await file.read()
            text = contents.decode("utf-8", errors="ignore")

        if not text or not text.strip():
            raise ValueError("The ingestion payload must include text or an uploaded file.")

        ingestor = get_ingestor()
        result = ingestor.ingest_text(text)
        return {"success": True, "detail": result}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("Failed to ingest document")
        raise HTTPException(status_code=500, detail="Failed to ingest document.") from error


@app.post("/api/query")
async def query(question: str = Form(...)) -> dict[str, object]:
    """Query the local RAG system and return the generated answer."""
    if not question.strip():
        raise HTTPException(status_code=400, detail="The query payload must include a question.")

    try:
        vector_manager = get_vector_manager()
        retriever = vector_manager.get_retriever()
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    try:
        rag_service = RAGService(settings, retriever)
        answer = rag_service.answer_question(question)
        return {"success": True, "question": question, "answer": answer}
    except Exception as error:
        logger.exception("Failed to generate answer")
        raise HTTPException(status_code=500, detail="Failed to generate an answer.") from error


@app.get("/")
def home():
    """Serve the frontend homepage HTML file."""
    return FileResponse("app/static/index.html")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
