"""
Topic route handlers.
GET /api/topics          – list all topics (card view)
GET /api/topics/{id}     – full topic detail with summary and key info
GET /api/topics/{id}/audio – stream the topic's MP3 audio
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config import settings
from models.schemas import TopicCardResponse, TopicDetailResponse, KeyInfo
from pipeline.content_processor import load_cached
from pipeline.tts_generator import audio_exists, audio_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=list[TopicCardResponse])
async def list_topics():
    """Return a list of all available legal topics as cards."""
    topics: list[TopicCardResponse] = []

    for topic_id, meta in settings.TOPIC_METADATA.items():
        # Try to get description from cache (may have AI-generated desc)
        cached = load_cached(topic_id)
        description = (
            cached.description if cached else meta.get("description", "")
        )

        topics.append(
            TopicCardResponse(
                id=topic_id,
                name=meta.get("name", topic_id.replace("_", " ").title()),
                description=description,
                icon=meta.get("icon", "BookOpen"),
            )
        )

    return topics


@router.get("/{topic_id}", response_model=TopicDetailResponse)
async def get_topic_detail(topic_id: str):
    """Return full details for a specific topic including summary and key info."""
    # Validate topic exists
    if topic_id not in settings.TOPIC_METADATA:
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic_id}' not found.",
        )

    cached = load_cached(topic_id)
    if cached is None:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Topic '{topic_id}' is still being processed. "
                "Please try again shortly."
            ),
        )

    return TopicDetailResponse(
        id=cached.topic_id,
        name=cached.name,
        description=cached.description,
        summary=cached.summary,
        key_info=cached.key_info,
        has_audio=audio_exists(topic_id),
    )


@router.get("/{topic_id}/audio")
async def get_topic_audio(topic_id: str):
    """Stream the MP3 audio file for a topic's summary."""
    if topic_id not in settings.TOPIC_METADATA:
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic_id}' not found.",
        )

    path = audio_path(topic_id)
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Audio not available for topic '{topic_id}'.",
        )

    return FileResponse(
        path=str(path),
        media_type="audio/mpeg",
        filename=f"{topic_id}.mp3",
    )
