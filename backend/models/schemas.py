"""
Pydantic models for all API request/response schemas.
"""

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Topic Schemas
# ──────────────────────────────────────────────

class TopicCardResponse(BaseModel):
    """Lightweight topic card for listing."""
    id: str
    name: str
    description: str
    icon: str


class KeyInfo(BaseModel):
    """Structured key information extracted from a legal topic."""
    rights: list[str] = Field(default_factory=list)
    provisions: list[str] = Field(default_factory=list)
    penalties: list[str] = Field(default_factory=list)
    beneficiaries: list[str] = Field(default_factory=list)


class TopicDetailResponse(BaseModel):
    """Full topic detail including summary and key info."""
    id: str
    name: str
    description: str
    summary: str
    key_info: KeyInfo
    has_audio: bool


# ──────────────────────────────────────────────
# Chat Schemas
# ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in the chat history."""
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    """Incoming chat request body."""
    question: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Chat response with answer and source citations."""
    answer: str
    sources: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Cache Schemas (internal use for JSON serialization)
# ──────────────────────────────────────────────

class TopicCache(BaseModel):
    """Cached AI-generated content for a topic."""
    topic_id: str
    name: str
    description: str
    icon: str
    summary: str
    key_info: KeyInfo
    has_audio: bool = False
