"""
Content processor: uses Google Gemini to generate summaries,
extract key legal information, and produce card descriptions.
Results are cached to JSON to avoid re-generation.
Includes retry logic with exponential backoff for rate limits.
"""

import asyncio
import json
import logging
from pathlib import Path

import google.generativeai as genai

from config import settings
from models.schemas import KeyInfo, TopicCache

logger = logging.getLogger(__name__)

# Rate limiting: delay between API calls (seconds)
API_CALL_DELAY = 5
MAX_RETRIES = 5
INITIAL_BACKOFF = 10  # seconds


def _get_model() -> genai.GenerativeModel:
    """Configure and return a Gemini generative model instance."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(settings.GEMINI_MODEL)


def _cache_path(topic_id: str) -> Path:
    """Return the path to the cache JSON file for a given topic."""
    return settings.CACHE_DIR / f"{topic_id}.json"


def is_cached(topic_id: str) -> bool:
    """Check whether processed content is already cached for a topic."""
    return _cache_path(topic_id).exists()


def load_cached(topic_id: str) -> TopicCache | None:
    """Load cached topic data from disk, or return None."""
    path = _cache_path(topic_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return TopicCache(**data)
    except Exception as e:
        logger.error("Failed to load cache for %s: %s", topic_id, e)
        return None


def save_cache(cache: TopicCache) -> None:
    """Persist topic cache to disk as JSON."""
    path = _cache_path(cache.topic_id)
    path.write_text(cache.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Saved cache for '%s'", cache.topic_id)


async def _call_gemini_with_retry(model: genai.GenerativeModel, prompt: str) -> str:
    """Call Gemini with exponential backoff retry on rate limit errors."""
    for attempt in range(MAX_RETRIES):
        try:
            response = await model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = (
                "resource_exhausted" in error_str
                or "429" in error_str
                or "quota" in error_str
                or "rate" in error_str
            )
            if is_rate_limit and attempt < MAX_RETRIES - 1:
                wait_time = INITIAL_BACKOFF * (2 ** attempt)
                logger.warning(
                    "Rate limited (attempt %d/%d). Waiting %ds before retry...",
                    attempt + 1, MAX_RETRIES, wait_time,
                )
                await asyncio.sleep(wait_time)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


async def generate_summary(model: genai.GenerativeModel, text: str) -> str:
    """
    Generate a concise summary (≤250 words) of a legal text using Gemini.
    """
    prompt = (
        "You are a legal expert summarizing Indian law for the general public.\n"
        "Summarize the following legal text in 250 words or fewer. "
        "Use clear, simple language. Cover the purpose, scope, and most "
        "important provisions of the law.\n\n"
        f"LEGAL TEXT:\n{text[:8000]}\n\n"
        "SUMMARY:"
    )
    try:
        return await _call_gemini_with_retry(model, prompt)
    except Exception as e:
        logger.error("Summary generation failed: %s", e)
        return "Summary could not be generated at this time."


async def extract_key_info(
    model: genai.GenerativeModel, text: str
) -> KeyInfo:
    """
    Extract structured key information from legal text using Gemini.
    Returns rights, provisions, penalties, and beneficiaries.
    """
    prompt = (
        "You are a legal expert analyzing Indian law.\n"
        "Extract the following from the legal text below and return them as "
        "a JSON object with exactly these keys:\n"
        '  "rights": list of key rights granted (3-6 items)\n'
        '  "provisions": list of important provisions (3-6 items)\n'
        '  "penalties": list of penalties for violations (3-6 items)\n'
        '  "beneficiaries": list of who benefits from this law (2-4 items)\n\n'
        "Each item should be a short, clear sentence (max 20 words).\n"
        "Return ONLY the JSON object, no other text.\n\n"
        f"LEGAL TEXT:\n{text[:8000]}\n\n"
        "JSON:"
    )
    try:
        raw = await _call_gemini_with_retry(model, prompt)
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        return KeyInfo(
            rights=data.get("rights", []),
            provisions=data.get("provisions", []),
            penalties=data.get("penalties", []),
            beneficiaries=data.get("beneficiaries", []),
        )
    except Exception as e:
        logger.error("Key info extraction failed: %s", e)
        return KeyInfo(
            rights=["Information not available"],
            provisions=["Information not available"],
            penalties=["Information not available"],
            beneficiaries=["General public"],
        )


async def generate_card_description(
    model: genai.GenerativeModel, text: str, topic_name: str
) -> str:
    """Generate a short card description (1-2 sentences) for a topic."""
    prompt = (
        f"Write a concise, engaging 1-2 sentence description for a legal knowledge card about '{topic_name}'. "
        f"Base it on this text:\n{text[:2000]}\n\n"
        "The description should be informative and accessible to non-legal users. "
        "Return ONLY the description text, no quotes or extra formatting."
    )
    try:
        return await _call_gemini_with_retry(model, prompt)
    except Exception as e:
        logger.error("Card description generation failed: %s", e)
        return ""


async def process_topic(topic_id: str, raw_text: str) -> TopicCache:
    """
    Process a single topic: generate summary and extract key info.
    Uses cache if available, otherwise calls Gemini and saves results.

    Args:
        topic_id: The topic identifier (e.g. 'pocso_act').
        raw_text: The full raw legal text.

    Returns:
        TopicCache with all generated content.
    """
    # Check cache first
    cached = load_cached(topic_id)
    if cached is not None:
        logger.info("Using cached content for '%s'", topic_id)
        return cached

    logger.info("Processing topic '%s' with Gemini...", topic_id)
    metadata = settings.TOPIC_METADATA.get(topic_id, {})

    model = _get_model()

    # Generate summary first
    summary = await generate_summary(model, raw_text)
    # Rate limit pause
    await asyncio.sleep(API_CALL_DELAY)

    # Then extract key info
    key_info = await extract_key_info(model, raw_text)
    await asyncio.sleep(API_CALL_DELAY)

    # Generate AI card description
    card_desc = await generate_card_description(
        model, raw_text, metadata.get("name", topic_id)
    )
    description = card_desc if card_desc else metadata.get("description", "")

    cache = TopicCache(
        topic_id=topic_id,
        name=metadata.get("name", topic_id.replace("_", " ").title()),
        description=description,
        icon=metadata.get("icon", "BookOpen"),
        summary=summary,
        key_info=key_info,
        has_audio=False,
    )

    save_cache(cache)
    return cache


async def process_all_topics(
    raw_sources: dict[str, str],
) -> dict[str, TopicCache]:
    """
    Process all topics, generating summaries and key info.

    Args:
        raw_sources: dict mapping topic_id -> raw text.

    Returns:
        dict mapping topic_id -> TopicCache.
    """
    results: dict[str, TopicCache] = {}

    for topic_id, text in raw_sources.items():
        try:
            cache = await process_topic(topic_id, text)
            results[topic_id] = cache
        except Exception as e:
            logger.error(
                "Failed to process topic '%s': %s", topic_id, e
            )

    logger.info("Processed %d topics.", len(results))
    return results
