# YouTube Sentiment Analyzer

**Multi-agent AI system for analyzing YouTube video comments using LangGraph, BM25 retrieval, and hierarchical agent orchestration.**

## 🎯 Overview

This application uses a sophisticated multi-agent architecture to analyze YouTube videos by:
- Fetching video data, comments (with rich metadata), and transcripts
- Using BM25 retrieval for fast, keyword-based document search
- Coordinating specialized agents for research and analysis
- Streaming real-time progress to a React frontend

### Key Features

✅ **Multi-Agent System**: 3-tier hierarchical architecture with SuperSupervisor, Research Team, and Analysis Team
✅ **Real-Time Streaming**: Watch agents work in real-time via Server-Sent Events
✅ **BM25 Retrieval**: Fast, keyword-based retrieval (no embeddings needed)
✅ **Rich Metadata**: Comments include author, likes, and publication dates
✅ **Transcript Analysis**: Video transcripts enhance context and search
✅ **Functional Approach**: Pure functions, no classes
✅ **Type-Safe**: Full TypeScript frontend, Pydantic backend

## 🏗️ Architecture

### Multi-Agent Hierarchy

```
┌─────────────────────────────────────────┐
│        SuperSupervisor                  │
│     (Meta-level coordinator)            │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐    ┌─────▼──────┐
│ Research   │    │ Analysis   │
│   Team     │    │   Team     │
└─────┬──────┘    └─────┬──────┘
      │                 │
  ┌───┴───┐         ┌───┴───┐
  │       │         │       │
Video  Comment   Sentiment Topic
Search  Finder    Agent   Agent
```

### Tech Stack

**Backend:**
- FastAPI (Python)
- LangGraph (multi-agent orchestration)
- LangChain (agent framework)
- BM25Retriever (keyword-based retrieval)
- OpenAI GPT models
- YouTube Data API v3
- Tavily Search API

**Frontend:**
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- Server-Sent Events (SSE)

## 📁 Project Structure

```
youtube-sentiment-chatbot/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, state, prompts
│   │   ├── youtube/        # Data collection (comments, transcript)
│   │   ├── rag/            # BM25 retrieval + generation
│   │   ├── agents/         # Agent factory, supervisors, tools
│   │   ├── graphs/         # LangGraph definitions
│   │   ├── api/            # FastAPI routes and models
│   │   ├── utils/          # Helper functions
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   └── lib/            # API client, types
│   ├── package.json
│   └── .env.local.example
└── notebooks/
    └── multi_agent_sentiment_analyzer.ipynb  # Original notebook
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys:
  - OpenAI API key
  - YouTube Data API v3 key
  - Tavily Search API key

### Backend Setup

#### Option 1: Using `uv` (Recommended - 10-100x Faster!)

```bash
# Install uv if you haven't already
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to backend
cd youtube-sentiment-chatbot/backend

# Install dependencies (creates .venv automatically)
uv sync

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run server
uv run uvicorn app.main:app --reload --port 8000
```

#### Option 2: Using `pip` (Traditional)

```bash
# Navigate to backend
cd youtube-sentiment-chatbot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend
cd youtube-sentiment-chatbot/frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.local.example .env.local

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📖 Usage

1. Open http://localhost:3000 in your browser
2. Enter a YouTube URL (e.g., `https://www.youtube.com/watch?v=VIDEO_ID`)
3. Adjust parameters:
   - **Max Comments**: 10-200 (default: 50)
   - **Question**: Customize what to analyze
4. Click **"Analyze Video"**
5. Watch the multi-agent system work in real-time:
   - **Progress**: System updates
   - **VideoSearch**: External web search with video context
   - **CommentFinder**: RAG retrieval over comments + transcript
   - **Sentiment**: Sentiment analysis with reflection
   - **Topic**: Topic extraction with reflection
6. View the final analysis and retrieved documents

## 🔑 API Keys Setup

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### YouTube Data API Key
1. Go to https://console.cloud.google.com/
2. Enable YouTube Data API v3
3. Create credentials (API key)
4. Add to `.env`: `YOUTUBE_API_KEY=...`

### Tavily Search API Key
1. Go to https://tavily.com/
2. Sign up and get API key
3. Add to `.env`: `TAVILY_API_KEY=...`

## 🎨 Features in Detail

### Multi-Agent Orchestration

**Research Team:**
- **VideoSearch Agent**: Uses Tavily to find external information (reviews, discussions) enhanced with video context
- **CommentFinder Agent**: Uses BM25 RAG to retrieve specific comments and transcript sections
- **ResearchSupervisor**: Routes between agents based on query requirements

**Analysis Team:**
- **Sentiment Agent**: Analyzes sentiment with reflection tool for quality assurance
- **Topic Agent**: Extracts topics with reflection tool for completeness
- **AnalysisSupervisor**: Coordinates analysis workflow

**SuperSupervisor:**
- Routes between Research and Analysis teams
- Coordinates overall workflow
- Returns comprehensive results

### BM25 Retrieval

- **Fast**: No embeddings needed, pure keyword matching
- **In-memory**: BM25Retriever from LangChain Community
- **Document Preparation**:
  - Video context chunked (750 chars, 150 overlap)
  - Comments kept whole (no chunking)
  - Metadata preserved (author, likes, dates)

### Streaming Architecture

- **Server-Sent Events (SSE)**: Real-time progress updates
- **Event Types**:
  - `progress`: System updates
  - `agent_message`: Agent outputs
  - `final`: Complete analysis with documents
  - `error`: Error messages

## 🧪 Testing

### Backend Health Check

```bash
curl http://localhost:8000/api/health
```

### Analyze Video (cURL)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "max_comments": 50,
    "question": "What is the overall sentiment?"
  }'
```

## 📚 Documentation

- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **Original Notebook**: [notebooks/multi_agent_sentiment_analyzer.ipynb](notebooks/multi_agent_sentiment_analyzer.ipynb)

## 🎓 Design Principles

1. **Preserve Notebook Logic**: All 20+ functions from the original notebook extracted exactly
2. **Functional Approach**: No classes, pure functions following open_deep_library pattern
3. **Modular Structure**: Each concern in its own module
4. **Type Safety**: TypedDict for Python, TypeScript for frontend
5. **Async/Streaming**: Real-time user experience
6. **Metadata Preservation**: Comments include author, likes, dates for rich analysis

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version (3.10+)
- Verify all API keys in `.env`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't connect:**
- Ensure backend is running on port 8000
- Check CORS is enabled in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**YouTube API quota exceeded:**
- YouTube API has daily quotas
- Use sparingly during development
- Consider caching analyzed videos

**No streaming events:**
- Check browser console for errors
- Verify backend `/api/analyze` endpoint
- Test with cURL first

## ⚡ Why Use `uv`?

`uv` is a blazing-fast Python package installer and resolver written in Rust:

- **10-100x faster** than pip
- **Automatic virtual environment** creation
- **Lock file** for reproducible installs
- **Drop-in replacement** for pip
- **Zero configuration** needed

Learn more: https://docs.astral.sh/uv/

## 🚧 Future Enhancements

- [ ] Database for persistent storage
- [ ] Caching for analyzed videos
- [ ] Follow-up query endpoint
- [ ] Sentiment visualization (charts)
- [ ] Analysis history
- [ ] Export results (PDF, CSV)
- [ ] Authentication
- [ ] Rate limiting
- [ ] Deployment guides (Docker, Vercel, AWS)

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built on LangGraph and LangChain frameworks
- Inspired by the open_deep_library pattern
- Uses OpenAI GPT models for LLM reasoning
- YouTube Data API for video data
- Tavily for web search

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check documentation in `backend/` and `frontend/` READMEs
- Review API docs at http://localhost:8000/docs

---

**Built with ❤️ using LangGraph, FastAPI, Next.js, and BM25**
