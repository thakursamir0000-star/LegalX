"""
Content loader: reads legal text files and splits them into chunks
using LangChain text splitters for downstream embedding and RAG.
"""

import logging
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import settings

logger = logging.getLogger(__name__)


def _topic_id_from_filename(filename: str) -> str:
    """Derive a topic ID from a filename (strip .txt extension)."""
    return Path(filename).stem


def load_source_documents() -> dict[str, str]:
    """
    Load all .txt files from the sources directory.

    Returns:
        dict mapping topic_id -> full raw text content.
    """
    sources: dict[str, str] = {}
    sources_dir = settings.SOURCES_DIR

    if not sources_dir.exists():
        logger.error("Sources directory does not exist: %s", sources_dir)
        return sources

    for filepath in sorted(sources_dir.glob("*.txt")):
        topic_id = _topic_id_from_filename(filepath.name)
        try:
            text = filepath.read_text(encoding="utf-8")
            sources[topic_id] = text
            logger.info(
                "Loaded source '%s' (%d chars)", topic_id, len(text)
            )
        except Exception as e:
            logger.error("Failed to load %s: %s", filepath.name, e)

    logger.info("Loaded %d source documents total.", len(sources))
    return sources


def chunk_documents(
    raw_sources: dict[str, str],
) -> dict[str, list[Document]]:
    """
    Split each raw source text into overlapping chunks.

    Args:
        raw_sources: dict mapping topic_id -> full text.

    Returns:
        dict mapping topic_id -> list of LangChain Document objects
        with metadata including topic_id and chunk_index.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: dict[str, list[Document]] = {}

    for topic_id, text in raw_sources.items():
        raw_chunks = splitter.split_text(text)
        docs = [
            Document(
                page_content=chunk,
                metadata={
                    "topic_id": topic_id,
                    "chunk_index": idx,
                    "source": f"{topic_id}.txt",
                },
            )
            for idx, chunk in enumerate(raw_chunks)
        ]
        all_chunks[topic_id] = docs
        logger.info(
            "Split '%s' into %d chunks", topic_id, len(docs)
        )

    total = sum(len(v) for v in all_chunks.values())
    logger.info("Total chunks across all topics: %d", total)
    return all_chunks
