"""Vector store ingestion and retrieval helpers for the local RAG application."""

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.document import Document

from app.services.settings import Settings


class DocumentIngestor:
    """Ingest raw text or files into a persistent Chroma vector store."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self.persist_directory = Path(settings.persist_directory)

    def ingest_text(self, text: str) -> dict[str, Any]:
        """Split text into chunks, embed them, and persist them to Chroma."""
        if not text or not text.strip():
            raise ValueError("No text provided for ingestion.")

        if not self.persist_directory.exists():
            self.persist_directory.mkdir(parents=True, exist_ok=True)

        document = Document(page_content=text)
        chunks = self.text_splitter.split_documents([document])

        if not chunks:
            raise ValueError("Ingestion produced no document chunks.")

        if any(self.persist_directory.iterdir()):
            vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
            )
            vector_store.add_documents(chunks)
        else:
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory),
            )

        vector_store.persist()
        return {
            "ingested_chunks": len(chunks),
            "persist_directory": str(self.persist_directory),
        }

    def ingest_file(self, file_path: str) -> dict[str, Any]:
        """Ingest a document from disk by loading and chunking its contents."""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")

        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        if not chunks:
            raise ValueError("Ingestion produced no document chunks.")

        if not self.persist_directory.exists():
            self.persist_directory.mkdir(parents=True, exist_ok=True)

        if any(self.persist_directory.iterdir()):
            vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
            )
            vector_store.add_documents(chunks)
        else:
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory),
            )

        vector_store.persist()
        return {
            "ingested_chunks": len(chunks),
            "persist_directory": str(self.persist_directory),
        }


class VectorStoreManager:
    """Manage loading and retrieving from the persisted Chroma vector store."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.model_name)
        self.persist_directory = Path(settings.persist_directory)

    def _validate_store(self) -> None:
        """Raise if the persistent vector store is missing or empty."""
        if not self.persist_directory.exists() or not any(self.persist_directory.iterdir()):
            raise FileNotFoundError(
                f"No vector store found in '{self.persist_directory}'. Run ingestion first."
            )

    def load_vector_store(self) -> Chroma:
        """Load the persisted Chroma vector store with current embeddings."""
        self._validate_store()
        return Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
        )

    def get_retriever(self) -> Any:
        """Create and return a retriever for RAG-style similarity search."""
        vector_store = self.load_vector_store()
        return vector_store.as_retriever(search_kwargs={"k": self.settings.retriever_k})
