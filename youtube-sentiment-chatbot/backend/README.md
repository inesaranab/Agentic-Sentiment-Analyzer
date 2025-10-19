# YouTube Sentiment Analyzer - Backend

Multi-agent sentiment analysis system for YouTube videos using FastAPI, LangGraph, and BM25 retrieval.

## Architecture

```
app/
├── core/                 # Core configuration and state
│   ├── configuration.py  # System configuration
│   ├── state.py          # TypedDict state definitions
│   └── prompts.py        # Agent and supervisor prompts
├── youtube/              # YouTube data collection
│   ├── collectors.py     # Fetch comments, details, transcript
│   └── document_builder.py # Create unified documents
├── rag/                  # Retrieval-Augmented Generation
│   ├── chunking.py       # Document preparation for BM25
│   ├── retrieval.py      # BM25 retrieval
│   └── generation.py     # LLM response generation
├── agents/               # Multi-agent system
│   ├── agent_factory.py  # Agent creation and node wrappers
│   ├── supervisor.py     # Team supervisor creation
│   ├── research_tools.py # VideoSearch & CommentFinder tools
│   └── analysis_tools.py # Sentiment & Topic reflection tools
├── graphs/               # LangGraph definitions
│   ├── rag_graph.py      # BM25 RAG graph
│   ├── research_graph.py # Research Team graph
│   ├── analysis_graph.py # Analysis Team graph
│   └── main_graph.py     # SuperSupervisor meta-graph
├── api/                  # FastAPI routes and models
│   ├── models.py         # Pydantic request/response models
│   └── routes.py         # API endpoints
├── utils/                # Utility functions
│   └── helpers.py        # Helper utilities
└── main.py               # FastAPI application

## Multi-Agent System

### Hierarchical 3-Tier Architecture

**Meta-Level: SuperSupervisor**
- Coordinates Research and Analysis teams
- Routes based on task requirements

**Research Team**
- **VideoSearch Agent**: External web search (Tavily) with video context
- **CommentFinder Agent**: Internal RAG retrieval over comments + transcript
- **ResearchSupervisor**: Routes between agents

**Analysis Team**
- **Sentiment Agent**: Sentiment analysis with reflection
- **Topic Agent**: Topic extraction with reflection
- **AnalysisSupervisor**: Routes between agents

## Data Flow

1. **YouTube Data Collection**
   - Fetch comments (with author, likes, dates metadata)
   - Fetch video details (title, channel, views, likes)
   - Fetch transcript

2. **Document Preparation**
   - Create unified document with all context
   - Chunk transcript (750 chars, 150 overlap)
   - Keep comments as individual documents (no chunking)
   - Combine into `docs_for_store` for BM25

3. **BM25 Retrieval**
   - Keyword-based retrieval
   - Fast, in-memory
   - No embeddings needed

4. **Multi-Agent Orchestration**
   - SuperSupervisor receives question
   - Routes to Research Team (gather data)
   - Routes to Analysis Team (analyze sentiment/topics)
   - Returns comprehensive response

## Installation

### Option 1: Using `uv` (Recommended - Much Faster!)

```bash
# Install uv if you haven't already
# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies (one command!)
uv sync

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Option 2: Using `pip` (Traditional)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Required API Keys

- `OPENAI_API_KEY` - OpenAI (GPT models)
- `YOUTUBE_API_KEY` - YouTube Data API v3
- `TAVILY_API_KEY` - Tavily Search
- `LANGCHAIN_API_KEY` - (Optional) LangSmith tracing

## Usage

### Run Server

```bash
# With uv (recommended)
uv run uvicorn app.main:app --reload --port 8000

# Or activate venv first, then run normally
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Or using the main module
python -m app.main
```

### API Endpoints

**POST /api/analyze**
- Analyze a YouTube video
- Streams progress and results via Server-Sent Events (SSE)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "max_comments": 50,
    "question": "What is the overall sentiment?"
  }'
```

**GET /api/health**
- Health check endpoint

**GET /docs**
- Interactive API documentation (Swagger UI)

## Configuration

Edit `app/core/configuration.py` or use environment variables:

- `generator_model`: Model for RAG generation (default: gpt-4.1-nano)
- `research_model`: Model for research agents (default: gpt-4o-mini)
- `analysis_model`: Model for analysis agents (default: gpt-4o-mini)
- `max_comments`: Max comments to fetch (default: 50)
- `chunk_size`: Text splitter chunk size (default: 750)
- `max_iterations`: Graph recursion limit (default: 100)

## Streaming Response Format

The API streams JSON events:

```json
{"type": "progress", "content": "Fetching video data..."}
{"type": "agent_message", "agent": "VideoSearch", "content": "..."}
{"type": "final", "content": "...", "documents": [...]}
{"type": "error", "content": "Error message"}
```

## Development

### Project Structure Principles

- **Functional approach**: No classes, pure functions
- **Modular**: Each function in its own logical module
- **Preserves notebook logic**: All functions from original notebook maintained
- **Async-ready**: Uses async/await for streaming

### Key Preserved Logic

✅ All 20+ functions from notebook extracted exactly
✅ Comments metadata (author, likes, dates) preserved
✅ Transcript available for video understanding
✅ BM25 document preparation logic intact
✅ Multi-agent coordination patterns maintained
✅ Document preservation across graph boundaries

## Troubleshooting

**Import errors**: Make sure you're running from the backend directory
```bash
cd youtube-sentiment-chatbot/backend
python -m app.main
```

**API key errors**: Check your .env file has all required keys

**YouTube API quota**: YouTube API has daily quotas - use sparingly during development

## Next Steps

- [ ] Implement caching for analyzed videos
- [ ] Add database for persistent storage
- [ ] Implement /query endpoint for follow-up questions
- [ ] Add rate limiting
- [ ] Add authentication
- [ ] Deploy to production
