# 🏗️ LegalX - System Architecture Quick Reference

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   USER (Web Browser)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Frontend (React + Vite)                        │ │
│  │  • HomePage: 5 topic cards                            │ │
│  │  • TopicPage: Summary, Keys, Audio, Chat              │ │
│  │  • API Client: Fetch wrapper with error handling      │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                           ▼ HTTP API
┌──────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI + Uvicorn)                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Endpoints:                                         │   │
│  │  GET  /api/topics           → Topic list           │   │
│  │  GET  /api/topics/{id}      → Topic detail         │   │
│  │  GET  /api/topics/{id}/audio → MP3 audio           │   │
│  │  POST /api/topics/{id}/chat → Q&A response         │   │
│  │  GET  /api/health           → Status check         │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AI Processing Pipeline (Startup):                  │   │
│  │  1. Load: content_loader.py                         │   │
│  │  2. Chunk: RecursiveCharacterTextSplitter           │   │
│  │  3. Embed: GoogleGenerativeAIEmbeddings → ChromaDB  │   │
│  │  4. Process: Gemini (summary + key_info)            │   │
│  │  5. Audio: edge-tts → MP3 files                     │   │
│  │  6. Cache: Save to JSON files                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  AI Modules (Runtime):                              │   │
│  │  • Retriever: ChromaDB semantic search              │   │
│  │  • RAG: Context retrieval + Gemini answer           │   │
│  │  • Response: Structured JSON with sources           │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                    ▼                       ▼
        ┌───────────────────┐   ┌──────────────────┐
        │  Gemini API       │   │  ChromaDB        │
        │  • Embeddings     │   │  • Vector Store  │
        │  • LLM            │   │  • Retrieval     │
        │  • Summarization  │   │  • Persistent    │
        └───────────────────┘   └──────────────────┘
```

---

## Data Flow

### On Startup
```
/backend/data/sources/*.txt
         ▼
   content_loader.py
         ▼
   RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
         ▼
   77 Document chunks with metadata
         ▼
   ┌─────────────────────────────────────────┐
   │                                         │
   ▼                                         ▼
embeddings.py                        content_processor.py
   ▼                                         ▼
GoogleGenerativeAIEmbeddings          Gemini 2.0 Flash
   ▼                                         ▼
ChromaDB (vector storage)            TopicCache (JSON)
                                            ▼
                                    /backend/data/cache/
```

### On User Request
```
Browser Request
   ▼
FastAPI Router
   ▼
   ├─→ /api/topics
   │   └─→ Load from cache JSON
   │       └─→ Return card data
   │
   ├─→ /api/topics/{id}
   │   └─→ Load cached topic detail
   │       └─→ Return summary + key_info
   │
   ├─→ /api/topics/{id}/audio
   │   └─→ Stream MP3 file
   │       └─→ Return audio data
   │
   └─→ /api/topics/{id}/chat
       └─→ Retrieve relevant chunks from ChromaDB
           └─→ Build context with chat history
               └─→ Send to Gemini
                   └─→ Parse response for sources
                       └─→ Return answer + sources
```

---

## Key Components

### Backend Directory Structure

```
backend/
├── main.py              # FastAPI app + startup pipeline
├── config.py            # Settings, env variables, paths
├── requirements.txt     # Python dependencies
├── .env                 # API keys (GEMINI_API_KEY)
│
├── models/
│   └── schemas.py       # Pydantic models for API validation
│
├── pipeline/            # Content processing (startup)
│   ├── content_loader.py    # Load & chunk text
│   ├── content_processor.py # Generate summaries & key_info
│   ├── embeddings.py        # Create vector embeddings
│   └── tts_generator.py     # Generate MP3 audio
│
├── rag/                 # Retrieval Augmented Generation (runtime)
│   ├── vector_store.py      # ChromaDB management
│   └── retriever.py         # Semantic search + answer generation
│
├── routes/              # API endpoints
│   ├── topics.py        # GET /api/topics, /api/topics/{id}
│   └── chat.py          # POST /api/topics/{id}/chat
│
└── data/                # Data storage
    ├── sources/         # Raw legal text files (5 topics)
    ├── cache/           # Generated JSON (summaries, key_info)
    └── audio/           # Generated MP3 files
```

### Frontend Directory Structure

```
frontend/src/
├── App.jsx              # Routes & layout
├── index.css            # Design system & animations
│
├── pages/
│   ├── HomePage.jsx     # Hero + 5 topic cards
│   └── TopicPage.jsx    # Topic detail with tabs
│
├── components/
│   ├── Navbar.jsx       # Navigation bar
│   ├── TopicCard.jsx    # Glassmorphism card
│   ├── Summary.jsx      # AI summary display
│   ├── KeyInfo.jsx      # Key info cards
│   ├── AudioPlayer.jsx  # Custom audio player
│   ├── ChatAssistant.jsx # RAG chat interface
│   ├── SearchBar.jsx    # Topic search
│   └── LoadingSpinner.jsx # Loading animation
│
└── utils/
    └── api.js           # API client with error handling
```

---

## Processing Pipeline Details

### Step 1: Content Loading
**File:** `content_loader.py`
```python
• Read all *.txt files from backend/data/sources/
• Map filename → topic_id (pocso_act.txt → pocso_act)
• Load full text into memory
• Log file size and topic name
```

### Step 2: Text Chunking
**File:** `content_loader.py`
```python
• Use RecursiveCharacterTextSplitter
• Chunk size: 1000 characters
• Overlap: 200 characters
• Separators: ["\n\n", "\n", ". ", " ", ""]
• Create metadata: {topic_id, source, chunk_index}
• Result: ~77 total chunks across all 5 topics
```

### Step 3: Embeddings
**File:** `embeddings.py`
```python
• Use GoogleGenerativeAIEmbeddings (Gemini API)
• For each chunk: generate 768-dim embedding
• Store in ChromaDB with metadata
• Enable semantic similarity search
• Persist to disk: backend/chroma_db/
```

### Step 4: Content Generation
**File:** `content_processor.py`
```python
• For each topic:
  - Generate summary (≤250 words, simple language)
  - Extract key_info (rights, provisions, penalties, beneficiaries)
• Use Gemini 2.0 Flash for both tasks
• Cache results to JSON
• Subsequent startups use cache (no API calls)
```

### Step 5: Audio Generation
**File:** `tts_generator.py`
```python
• For each summary:
  - Convert to speech using edge-tts
  - Use en-US-AriaNeural voice
  - Generate MP3 file
• Save to: backend/data/audio/{topic_id}.mp3
• Graceful fallback if TTS API fails
```

### Step 6: RAG Q&A Setup
**File:** `retriever.py`
```python
• On user question:
  - Embed question using Gemini embeddings
  - Search ChromaDB for top-5 similar chunks
  - Filter by topic_id (stay in legal domain)
• Build context with retrieved chunks
• Pass to Gemini with prompt
• Extract source citations from response
```

---

## API Contracts

### GET /api/topics
```json
Response: [
  {
    "id": "pocso_act",
    "name": "POCSO Act",
    "description": "Protection of Children from Sexual Offences Act, 2012",
    "icon": "Shield"
  },
  ...
]
```

### GET /api/topics/{id}
```json
Response: {
  "id": "pocso_act",
  "name": "POCSO Act",
  "description": "...",
  "summary": "The POCSO Act is...",
  "key_info": {
    "rights": ["Children are protected..."],
    "provisions": ["Strict procedures..."],
    "penalties": ["Imprisonment up to..."],
    "beneficiaries": ["Children ≤18 years..."]
  },
  "has_audio": true
}
```

### POST /api/topics/{id}/chat
```json
Request: {
  "question": "What is the punishment under POCSO?",
  "history": [
    {"role": "user", "content": "What is POCSO?"},
    {"role": "assistant", "content": "POCSO is..."}
  ]
}

Response: {
  "answer": "Under POCSO, penalties range from 10 to 20 years...",
  "sources": ["pocso_act.txt"]
}
```

### GET /api/health
```json
Response: {
  "status": "healthy",
  "documents_indexed": 77,
  "topics_available": ["pocso_act", "consumer_protection_act", ...]
}
```

---

## Environment Variables

```bash
# Backend (.env file)
GEMINI_API_KEY=AIza...          # Required
GOOGLE_API_KEY=AIza...          # Optional backup
GEMINI_MODEL=gemini-2.0-flash   # Default
CHUNK_SIZE=1000                 # Characters
CHUNK_OVERLAP=200               # Characters
CORS_ORIGINS=["http://localhost:5173", ...]
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| First Startup Time | 2-5 minutes |
| Subsequent Startups | 30-60 seconds |
| Documents Indexed | 77 chunks |
| Topics Processed | 5 topics |
| API Response Time | <1 second |
| Chat Q&A Response | 2-3 seconds |
| Audio File Size | ~600 KB (MP3) |
| Database Size | ~10 MB (ChromaDB) |

---

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | User interface |
| **Backend** | FastAPI + Uvicorn | REST API |
| **LLM** | Gemini 2.0 Flash | Text generation |
| **Embeddings** | Gemini embeddings-001 | Vector embeddings |
| **Vector DB** | ChromaDB | Semantic search |
| **TTS** | edge-tts | Text to speech |
| **Framework** | LangChain | AI orchestration |
| **Deployment** | Docker | Containerization |

---

## Deployment Topology

```
Production:
  Frontend (Vercel)    ──HTTPS──▶  Backend (Railway)
  https://legalx.vercel.app        https://legalx-api.railway.app
  
  Backend (Railway)    ──HTTP──▶  Gemini API
                      ──HTTP──▶  ChromaDB (local)
```

---

## Security Considerations

1. **API Keys**
   - Stored in `.env` (not committed)
   - Environment variables in deployment
   - No hardcoding in code

2. **CORS**
   - Only allows frontend origin
   - Prevents cross-origin attacks

3. **Input Validation**
   - Pydantic schemas validate all inputs
   - Type hints throughout

4. **Error Handling**
   - Graceful failures (no crash on API error)
   - Safe error messages to client
   - Logging of all issues

---

## Quick Commands Reference

```bash
# Backend Startup
cd backend && python main.py

# Frontend Startup
cd frontend && npm run dev

# Docker Startup
docker-compose up --build

# Test API
curl http://localhost:8000/api/health

# Frontend Build
npm run build

# Verify Python version
python --version  # Must be 3.11+

# Verify Node version
node --version  # Must be 18+
```

---

## Troubleshooting Quick Reference

| Issue | Check | Solution |
|-------|-------|----------|
| Port already in use | `lsof -i :8000` | Kill process or use different port |
| Module not found | `pip install -r requirements.txt` | Install dependencies |
| API key invalid | `.env` file | Verify GEMINI_API_KEY is correct |
| Frontend won't load | Browser console F12 | Check API URL, CORS settings |
| No audio generated | Backend logs | edge-tts may have failed (graceful) |
| ChromaDB not found | `backend/chroma_db/` | Run pipeline again (recreates) |

---

**This is your LegalX system architecture at a glance!** 🏗️
