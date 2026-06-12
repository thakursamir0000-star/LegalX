"""
Chat route handler.
POST /api/topics/{id}/chat – RAG-powered conversational Q&A.
"""

import logging

from fastapi import APIRouter, HTTPException

from config import settings
from models.schemas import ChatRequest, ChatResponse
from rag.retriever import ask_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/topics", tags=["chat"])


@router.post("/{topic_id}/chat", response_model=ChatResponse)
async def chat_with_topic(topic_id: str, request: ChatRequest):
    """
    Answer a question about a legal topic using RAG.

    Retrieves relevant chunks from ChromaDB filtered by topic_id,
    passes them as context to Gemini along with the question and
    chat history, and returns the answer with source citations.
    """
    # Validate topic exists
    if topic_id not in settings.TOPIC_METADATA:
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic_id}' not found.",
        )

    logger.info(
        "Chat request for topic '%s': %s",
        topic_id,
        request.question[:80],
    )

    # Convert history to list of dicts for the retriever
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.history
    ]

    # Use RAG to answer
    result = await ask_question(
        topic_id=topic_id,
        question=request.question,
        history=history,
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
    )
