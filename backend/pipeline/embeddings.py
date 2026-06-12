"""
Embeddings pipeline: creates vector embeddings for document chunks
and stores them in a persistent ChromaDB collection via LangChain.
"""

import logging

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings
from rag.vector_store import get_or_create_vector_store

logger = logging.getLogger(__name__)


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    """Return the Google Generative AI embedding function."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )


async def build_embeddings(
    chunked_docs: dict[str, list[Document]],
) -> None:
    """
    Build embeddings for all document chunks and upsert them
    into the ChromaDB vector store.

    If the collection already contains documents for a topic,
    that topic is skipped to avoid duplicate embeddings.

    Args:
        chunked_docs: dict mapping topic_id -> list of Document chunks.
    """
    vector_store = get_or_create_vector_store()

    # Gather all documents to add
    all_docs: list[Document] = []
    all_ids: list[str] = []

    # Check which topics already have embeddings
    existing_collection = vector_store._collection
    existing_ids = set()
    try:
        existing_data = existing_collection.get()
        if existing_data and existing_data.get("ids"):
            existing_ids = set(existing_data["ids"])
    except Exception:
        pass

    for topic_id, docs in chunked_docs.items():
        for doc in docs:
            doc_id = f"{topic_id}_chunk_{doc.metadata['chunk_index']}"
            if doc_id in existing_ids:
                continue
            all_docs.append(doc)
            all_ids.append(doc_id)

    if not all_docs:
        logger.info("All embeddings already exist in ChromaDB. Skipping.")
        return

    logger.info(
        "Adding %d new document chunks to ChromaDB...", len(all_docs)
    )

    # Add in batches to avoid overwhelming the API
    batch_size = 50
    for i in range(0, len(all_docs), batch_size):
        batch_docs = all_docs[i : i + batch_size]
        batch_ids = all_ids[i : i + batch_size]
        vector_store.add_documents(documents=batch_docs, ids=batch_ids)
        logger.info(
            "Embedded batch %d-%d / %d",
            i + 1,
            min(i + batch_size, len(all_docs)),
            len(all_docs),
        )

    logger.info("Embedding pipeline complete.")
