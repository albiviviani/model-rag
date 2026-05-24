"""CLI helper for querying the local RAG service from the command line."""

import argparse
import sys

from app.services.rag_service import RAGService
from app.services.settings import Settings
from app.services.vector_store_service import VectorStoreManager


def main() -> int:
    """Parse CLI arguments, query the RAG system, and print the answer."""
    parser = argparse.ArgumentParser(
        description="Query the local RAG system using the persisted Chroma vector store."
    )
    parser.add_argument(
        "-q",
        "--question",
        required=True,
        help="The question to ask against the ingested document.",
    )
    args = parser.parse_args()

    settings = Settings()
    manager = VectorStoreManager(settings)

    try:
        retriever = manager.get_retriever()
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    rag_service = RAGService(settings, retriever)
    answer = rag_service.answer_question(args.question)
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
