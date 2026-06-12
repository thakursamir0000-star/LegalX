"""Quick script to generate audio files for all topics."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import settings, ensure_directories
from pipeline.content_processor import load_cached, save_cache
from pipeline.tts_generator import generate_all_audio


async def main():
    ensure_directories()
    
    summaries = {}
    for topic_id in settings.TOPIC_METADATA:
        cached = load_cached(topic_id)
        if cached and cached.summary and "could not be generated" not in cached.summary:
            summaries[topic_id] = cached.summary
            print(f"[OK] Found summary for {topic_id} ({len(cached.summary)} chars)")
        else:
            print(f"[SKIP] No valid summary for {topic_id}")
    
    print(f"\nGenerating audio for {len(summaries)} topics...")
    results = await generate_all_audio(summaries)
    
    for topic_id, success in results.items():
        cached = load_cached(topic_id)
        if cached:
            cached.has_audio = success
            save_cache(cached)
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {topic_id}")
    
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
