"""
RAG retriever: performs retrieval-augmented generation using ChromaDB
for context retrieval and Gemini for answer generation.
Includes retry logic with exponential backoff for rate limits.
"""

import asyncio
import logging

from google import genai

from config import settings
from rag.vector_store import get_or_create_vector_store

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
INITIAL_BACKOFF = 2  # seconds



def _get_client() -> genai.Client:
    """Configure and return a Gemini client instance."""
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def _call_gemini_with_retry(client: genai.Client, prompt: str) -> str:
    """Call Gemini with exponential backoff retry on rate limit errors."""
    for attempt in range(MAX_RETRIES):
        try:
            response = await client.aio.models.generate_content(
                model=settings.GEMINI_MODEL, contents=prompt
            )
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


def retrieve_relevant_chunks(
    topic_id: str, query: str, k: int = 5
) -> list[dict]:
    """
    Retrieve the most relevant document chunks from ChromaDB
    filtered by topic_id.

    Args:
        topic_id: The topic to filter by.
        query: The user's question.
        k: Number of top results to return.

    Returns:
        List of dicts with 'content' and 'source' keys.
    """
    vector_store = get_or_create_vector_store()

    try:
        results = vector_store.similarity_search(
            query=query,
            k=k,
            filter={"topic_id": topic_id},
        )

        chunks = []
        for doc in results:
            chunks.append(
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", -1),
                }
            )

        logger.info(
            "Retrieved %d chunks for topic '%s' (query: '%s')",
            len(chunks),
            topic_id,
            query[:60],
        )
        return chunks

    except Exception as e:
        logger.error("Retrieval failed for topic '%s': %s", topic_id, e)
        return []


def _build_chat_prompt(
    question: str,
    context_chunks: list[dict],
    history: list[dict],
) -> str:
    """
    Build the full prompt for Gemini including context and chat history.
    """
    # Format context
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(f"[Source {i}]: {chunk['content']}")
    context_text = "\n\n".join(context_parts)

    # Format chat history
    history_text = ""
    if history:
        history_lines = []
        for msg in history[-6:]:  # Keep last 6 messages for context
            role = msg.get("role", "user").capitalize()
            history_lines.append(f"{role}: {msg.get('content', '')}")
        history_text = "\n".join(history_lines)

    prompt = (
        "You are a knowledgeable Indian legal assistant. Answer the user's "
        "question based ONLY on the provided legal context. Be accurate, "
        "helpful, and use simple language that a layperson can understand.\n\n"
        "RULES:\n"
        "1. Only use information from the provided context.\n"
        "2. If the context doesn't contain enough information, say so honestly.\n"
        "3. Cite which source(s) you used (e.g., [Source 1], [Source 2]).\n"
        "4. Keep answers concise but thorough.\n"
        "5. Use bullet points or numbered lists when listing multiple items.\n\n"
    )

    if history_text:
        prompt += f"CHAT HISTORY:\n{history_text}\n\n"

    prompt += (
        f"LEGAL CONTEXT:\n{context_text}\n\n"
        f"USER QUESTION: {question}\n\n"
        "ANSWER:"
    )

    return prompt


def _extract_sources(
    context_chunks: list[dict], answer: str
) -> list[str]:
    """
    Extract source citations from the answer and context.
    Returns a list of unique source identifiers referenced.
    """
    sources = []
    seen = set()
    for i, chunk in enumerate(context_chunks, 1):
        source_tag = f"[Source {i}]"
        source_name = chunk.get("source", "unknown")
        if source_tag in answer and source_name not in seen:
            sources.append(source_name)
            seen.add(source_name)

    # If no explicit citations found, include all sources used for context
    if not sources:
        for chunk in context_chunks:
            source_name = chunk.get("source", "unknown")
            if source_name not in seen:
                sources.append(source_name)
                seen.add(source_name)

    return sources


def get_local_fallback(topic_id: str, question: str) -> str | None:
    """Provide a fallback answer from the pre-generated caches if Gemini fails."""
    try:
        from pipeline.content_processor import load_cached
        cached = load_cached(topic_id)
        if not cached or not cached.key_info:
            return None
        
        q = question.lower()
        key_info = cached.key_info
        
        if "provision" in q or "rules" in q or "law" in q:
            items = key_info.provisions
            if items:
                joined = "\n".join([f"* {item}" for item in items])
                return f"Based on the pre-processed records for the {cached.name}, here are the key provisions:\n\n{joined}"
        
        if "beneficiar" in q or "who" in q or "target" in q:
            items = key_info.beneficiaries
            if items:
                joined = "\n".join([f"* {item}" for item in items])
                return f"Under the {cached.name}, the primary beneficiaries are:\n\n{joined}"
                
        if "penalt" in q or "punish" in q or "fine" in q or "jail" in q:
            items = key_info.penalties
            if items:
                joined = "\n".join([f"* {item}" for item in items])
                return f"The {cached.name} defines the following penalties and punishments for offenses:\n\n{joined}"
                
        if "right" in q:
            items = key_info.rights
            if items:
                joined = "\n".join([f"* {item}" for item in items])
                return f"Here are the rights protected under the {cached.name}:\n\n{joined}"

                
        # General default fallback to summary for any other queries
        if cached.summary:
            return (
                f"I am currently operating in offline mode due to API rate limits, "
                f"but here is a comprehensive summary of the {cached.name}:\n\n{cached.summary}"
            )
                
    except Exception as e:
        logging.getLogger(__name__).error("Fallback failed: %s", e)
    
    return None



async def ask_question(
    topic_id: str,
    question: str,
    history: list[dict] | None = None,
) -> dict:
    """
    Answer a user's question using RAG: retrieve relevant chunks
    from ChromaDB, pass them as context to Gemini, and return
    the answer with source citations.

    Args:
        topic_id: The topic to query against.
        question: The user's question.
        history: Optional chat history.

    Returns:
        dict with 'answer' and 'sources' keys.
    """
    if history is None:
        history = []

    # Step 1: Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(topic_id, question)

    if not chunks:
        return {
            "answer": (
                "I don't have enough information about this topic to answer "
                "your question. Please try rephrasing or ask about a different "
                "aspect of this law."
            ),
            "sources": [],
        }

    # Step 2: Build the prompt with context
    prompt = _build_chat_prompt(question, chunks, history)

    # Step 3: Generate answer with Gemini (with retry)
    client = _get_client()
    try:
        answer = await _call_gemini_with_retry(client, prompt)
    except Exception as e:
        logger.error("Gemini generation failed: %s", e)
        # Try local cache fallback for common suggested questions
        fallback_answer = get_local_fallback(topic_id, question)
        if fallback_answer:
            logger.info("Using local cache fallback answer for query: %s", question)
            return {
                "answer": fallback_answer,
                "sources": [f"{topic_id}.txt"]
            }

        return {
            "answer": (
                f"I'm sorry, I encountered an error while processing your "
                f"question. Error details: {type(e).__name__}: {str(e)}"
            ),
            "sources": [],
        }

    # Step 4: Extract sources
    sources = _extract_sources(chunks, answer)

    logger.info(
        "Answered question for topic '%s': %d sources cited.",
        topic_id,
        len(sources),
    )

    return {"answer": answer, "sources": sources}

