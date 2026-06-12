"""
TTS generator: converts topic summaries to MP3 audio using gTTS.
Audio files are cached on disk to avoid re-generation.
"""

import logging
from pathlib import Path
from gtts import gTTS

from config import settings

logger = logging.getLogger(__name__)


def audio_path(topic_id: str) -> Path:
    """Return the path where the audio file for a topic should be stored."""
    return settings.AUDIO_DIR / f"{topic_id}.mp3"


def audio_exists(topic_id: str) -> bool:
    """Check if audio has already been generated for a topic."""
    path = audio_path(topic_id)
    return path.exists() and path.stat().st_size > 0


async def generate_audio(topic_id: str, text: str) -> bool:
    """
    Generate an MP3 audio file from text using Google Text-to-Speech (gTTS).

    Args:
        topic_id: The topic identifier.
        text: The text to convert to speech (typically the summary).

    Returns:
        True if audio was generated successfully, False otherwise.
    """
    if audio_exists(topic_id):
        logger.info("Audio already exists for '%s'. Skipping.", topic_id)
        return True

    output_path = audio_path(topic_id)
    logger.info("Generating audio for '%s'...", topic_id)

    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(str(output_path))
        logger.info(
            "Audio saved for '%s' (%d bytes)",
            topic_id,
            output_path.stat().st_size,
        )
        return True
    except Exception as e:
        logger.error("Audio generation failed for '%s': %s", topic_id, e)
        # Clean up partial file if it exists
        if output_path.exists():
            output_path.unlink()
        return False


async def generate_all_audio(
    topic_summaries: dict[str, str],
) -> dict[str, bool]:
    """
    Generate audio for all topic summaries.

    Args:
        topic_summaries: dict mapping topic_id -> summary text.

    Returns:
        dict mapping topic_id -> whether audio was generated successfully.
    """
    results: dict[str, bool] = {}

    for topic_id, summary in topic_summaries.items():
        success = await generate_audio(topic_id, summary)
        results[topic_id] = success

    generated = sum(1 for v in results.values() if v)
    logger.info(
        "Audio generation complete: %d/%d successful.",
        generated,
        len(results),
    )
    return results
