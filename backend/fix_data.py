"""Script to fix missing key_info and audio for all topics."""
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from config import settings, ensure_directories
from pipeline.content_processor import _get_model, _call_gemini_with_retry, save_cache, load_cached, extract_key_info
from pipeline.tts_generator import generate_all_audio
from models.schemas import KeyInfo

API_CALL_DELAY = 8


async def fix_key_info():
    """Re-extract key info for topics that have fallback data."""
    ensure_directories()
    model = _get_model()
    
    for topic_id in settings.TOPIC_METADATA:
        cached = load_cached(topic_id)
        if cached is None:
            print(f"[SKIP] No cache for {topic_id}")
            continue
        
        # Check if key_info has fallback data
        has_fallback = (
            cached.key_info.rights == ["Information not available"]
            or len(cached.key_info.rights) == 0
        )
        
        if not has_fallback:
            print(f"[OK] {topic_id} already has valid key_info")
            continue
        
        print(f"[FIX] Re-extracting key_info for {topic_id}...")
        
        # Load source text
        source_path = settings.SOURCES_DIR / f"{topic_id}.txt"
        if not source_path.exists():
            print(f"  [ERROR] Source file not found: {source_path}")
            continue
        
        raw_text = source_path.read_text(encoding="utf-8")
        
        try:
            key_info = await extract_key_info(model, raw_text)
            cached.key_info = key_info
            save_cache(cached)
            print(f"  [OK] Key info updated for {topic_id}")
            print(f"    Rights: {key_info.rights[:2]}...")
        except Exception as e:
            print(f"  [ERROR] Failed: {e}")
        
        await asyncio.sleep(API_CALL_DELAY)


async def fix_audio():
    """Generate audio for all topics."""
    ensure_directories()
    
    summaries = {}
    for topic_id in settings.TOPIC_METADATA:
        cached = load_cached(topic_id)
        if cached and cached.summary and "could not be generated" not in cached.summary:
            summaries[topic_id] = cached.summary
    
    if not summaries:
        print("[ERROR] No valid summaries found for audio generation")
        return
    
    print(f"\n[AUDIO] Generating audio for {len(summaries)} topics...")
    results = await generate_all_audio(summaries)
    
    for topic_id, success in results.items():
        cached = load_cached(topic_id)
        if cached:
            cached.has_audio = success
            save_cache(cached)
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {topic_id}")


async def main():
    print("=" * 50)
    print("LegalX Fix Script - Key Info & Audio")
    print("=" * 50)
    
    await fix_key_info()
    await fix_audio()
    
    print("\n" + "=" * 50)
    print("Fix script complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
