"""
ChromaDB vector store management.
Provides a singleton persistent ChromaDB collection via LangChain.
"""

import logging

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings

logger = logging.getLogger(__name__)

# Module-level singleton
_vector_store: Chroma | None = None

COLLECTION_NAME = "legal_knowledge"


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    """Return the configured embedding function."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )


def get_or_create_vector_store() -> Chroma:
    """
    Return the singleton ChromaDB vector store instance.
    Creates it if it doesn't exist yet with persistent storage.
    """
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    logger.info(
        "Initializing ChromaDB at %s (collection: %s)",
        settings.CHROMA_DIR,
        COLLECTION_NAME,
    )

    _vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=str(settings.CHROMA_DIR),
    )

    logger.info("ChromaDB vector store ready.")
    return _vector_store


def get_collection_count() -> int:
    """Return the number of documents in the vector store."""
    store = get_or_create_vector_store()
    try:
        return store._collection.count()
    except Exception:
        return 0
