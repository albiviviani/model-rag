"""CLI helper for ingesting documents into the local RAG vector store."""

import argparse
import sys
from pathlib import Path

from app.services.settings import Settings
from app.services.vector_store_service import DocumentIngestor


def main() -> int:
    """Parse CLI options and ingest a text document into the vector store."""
    parser = argparse.ArgumentParser(
        description="Ingest a text document into the local Chroma vector store."
    )
    parser.add_argument(
        "-f",
        "--file",
        default="data/sample_document.txt",
        help="Path to a text file to ingest.",
    )
    parser.add_argument(
        "--text",
        help="Text to ingest directly. If provided, this takes precedence over --file.",
    )

    args = parser.parse_args()
    settings = Settings()
    ingestor = DocumentIngestor(settings)

    if args.text:
        text = args.text.strip()
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: Document not found at {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8").strip()

    if not text:
        print("Error: No text was provided for ingestion.", file=sys.stderr)
        return 1

    result = ingestor.ingest_text(text)
    print(
        f"Ingested {result['ingested_chunks']} chunk(s) into {result['persist_directory']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
