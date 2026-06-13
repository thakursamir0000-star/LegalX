"""
LegalX AI Knowledge Centre – FastAPI Application Entry Point.

On startup, runs the full AI pipeline:
1. Load legal source texts
2. Split into chunks
3. Generate embeddings and store in ChromaDB
4. Generate summaries and key info via Gemini (cached)
5. Generate audio via edge-tts (cached)

Then serves the API for the frontend.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings, ensure_directories
from pipeline.content_loader import load_source_documents, chunk_documents
from pipeline.content_processor import process_all_topics, save_cache
from pipeline.embeddings import build_embeddings
from pipeline.tts_generator import generate_all_audio, audio_exists
from rag.vector_store import get_collection_count
from routes.topics import router as topics_router
from routes.chat import router as chat_router

# ──────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("legalx")


# ──────────────────────────────────────────────
# Startup pipeline
# ──────────────────────────────────────────────
async def run_pipeline() -> None:
    """Execute the full content processing pipeline."""
    logger.info("=" * 60)
    logger.info("  LegalX AI Knowledge Centre - Pipeline Starting")
    logger.info("=" * 60)

    # Step 0: Ensure directories exist
    ensure_directories()
    logger.info("[OK] Directories verified.")

    # Step 1: Load source documents
    logger.info("--- Step 1: Loading source documents ---")
    raw_sources = load_source_documents()
    if not raw_sources:
        logger.error("No source documents found! Pipeline aborted.")
        return
    logger.info("[OK] Loaded %d source documents.", len(raw_sources))

    # Step 2: Chunk documents
    logger.info("--- Step 2: Chunking documents ---")
    chunked_docs = chunk_documents(raw_sources)
    total_chunks = sum(len(v) for v in chunked_docs.values())
    logger.info("[OK] Created %d chunks total.", total_chunks)

    # Step 3: Build embeddings
    logger.info("--- Step 3: Building embeddings ---")
    await build_embeddings(chunked_docs)
    count = get_collection_count()
    logger.info("[OK] ChromaDB has %d documents.", count)

    # Step 4: Process topics with Gemini (summaries + key info)
    logger.info("--- Step 4: Processing topics with Gemini ---")
    topic_caches = await process_all_topics(raw_sources)
    logger.info("[OK] Processed %d topics.", len(topic_caches))

    # Step 5: Generate audio
    logger.info("--- Step 5: Generating audio ---")
    summaries = {
        tid: cache.summary for tid, cache in topic_caches.items()
    }
    audio_results = await generate_all_audio(summaries)

    # Update caches with audio availability
    for tid, success in audio_results.items():
        if tid in topic_caches:
            topic_caches[tid].has_audio = success
            save_cache(topic_caches[tid])

    logger.info("[OK] Audio generation complete.")

    logger.info("=" * 60)
    logger.info("  Pipeline Complete - API is ready!")
    logger.info("=" * 60)


# ──────────────────────────────────────────────
# Application lifespan
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the pipeline in the background on startup, cleanup on shutdown."""
    import asyncio
    # Run heavy startup pipeline in background to prevent blocking port binding
    asyncio.create_task(run_pipeline())
    yield
    logger.info("LegalX backend shutting down.")



# ──────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────
app = FastAPI(
    title="LegalX AI Knowledge Centre",
    description=(
        "AI-powered legal knowledge platform providing summaries, "
        "key information, and conversational Q&A for Indian legal topics."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(topics_router)
app.include_router(chat_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    doc_count = get_collection_count()
    key = settings.GEMINI_API_KEY or ""
    return {
        "status": "healthy",
        "documents_indexed": doc_count,
        "topics_available": list(settings.TOPIC_METADATA.keys()),
        "gemini_api_key_configured": bool(key),
        "gemini_api_key_length": len(key),
        "gemini_api_key_prefix": key[:6] if key else "",
        "gemini_api_key_suffix": key[-4:] if key else "",
    }



# ──────────────────────────────────────────────
# Direct execution
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info",
    )
