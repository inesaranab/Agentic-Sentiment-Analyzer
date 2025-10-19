# Quick Start with `uv` ⚡

The fastest way to get started with the YouTube Sentiment Analyzer!

## Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys ready (OpenAI, YouTube, Tavily)

## Step 1: Install `uv`

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verify Installation
```bash
uv --version
```

## Step 2: Backend Setup (2 commands!)

```bash
# Navigate to backend
cd youtube-sentiment-chatbot/backend

# Install all dependencies (creates .venv automatically!)
uv sync
```

That's it! `uv` automatically:
- Creates a virtual environment in `.venv/`
- Installs all dependencies from `pyproject.toml`
- Generates a lock file for reproducibility

## Step 3: Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
# Use your favorite editor (nano, vim, code, notepad, etc.)
```

Required keys in `.env`:
```env
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=...
TAVILY_API_KEY=...
```

## Step 4: Run Backend

```bash
# Run with uv (no need to activate venv!)
uv run uvicorn app.main:app --reload --port 8000
```

Backend is now running at: http://localhost:8000

## Step 5: Frontend Setup

Open a **new terminal** window:

```bash
# Navigate to frontend
cd youtube-sentiment-chatbot/frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend is now running at: http://localhost:3000

## Step 6: Use the App!

1. Open http://localhost:3000
2. Paste a YouTube URL
3. Click "Analyze Video"
4. Watch the agents work in real-time! 🎉

## Common `uv` Commands

```bash
# Install dependencies
uv sync

# Add a new package
uv add package-name

# Remove a package
uv remove package-name

# Update dependencies
uv lock --upgrade

# Run any command in the virtual environment
uv run <command>

# Activate the virtual environment manually (if needed)
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

## Why `uv` is Amazing

- **⚡ 10-100x faster** than pip
- **🔒 Reproducible** with automatic lock file
- **🎯 Zero config** - just works
- **🔄 Drop-in replacement** for pip/venv
- **🦀 Written in Rust** - blazing fast

## Troubleshooting

**`uv` command not found:**
- Restart your terminal after installation
- Or add to PATH manually

**Dependencies not installing:**
- Check Python version: `python --version` (should be 3.10+)
- Try: `uv sync --reinstall`

**Backend won't start:**
- Make sure `.env` file exists with API keys
- Check if port 8000 is already in use

**Frontend won't connect:**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local` (optional)

## Next Steps

- Check out the full [README.md](README.md)
- Read the [Backend Documentation](backend/README.md)
- Read the [Frontend Documentation](frontend/README.md)

---

**Total setup time with `uv`: ~2 minutes** ⚡🚀
