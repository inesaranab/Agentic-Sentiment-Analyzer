"""Main FastAPI application for YouTube Sentiment Analyzer.

This module initializes and configures the FastAPI app with:
- CORS middleware for frontend communication
- API routes
- Error handling
"""

from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="YouTube Sentiment Analyzer",
    description="Multi-agent sentiment analysis system for YouTube videos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",  # Alternative port
        "http://localhost:3002",  # Alternative port 2
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["analysis"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "YouTube Sentiment Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
