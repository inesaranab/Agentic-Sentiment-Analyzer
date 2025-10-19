"""Pydantic models for API requests and responses.

This module defines request and response models for:
- Video analysis endpoint
- Query endpoint
- Streaming responses
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class VideoAnalysisRequest(BaseModel):
    """Request model for video analysis endpoint."""

    url: str = Field(
        ...,
        description="YouTube video URL or video ID",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"]
    )

    max_comments: int = Field(
        default=50,
        description="Maximum number of comments to fetch",
        ge=1,
        le=200
    )

    question: Optional[str] = Field(
        default="What is the overall sentiment of the comments on this video?",
        description="Initial question to ask about the video"
    )


class QueryRequest(BaseModel):
    """Request model for follow-up queries on analyzed videos.
    
    Use session_id from a previous /analyze call to ask follow-up
    questions within the same conversation thread.
    """

    session_id: str = Field(
        ...,
        description="Session ID (thread_id) from a previous analysis",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    )

    question: str = Field(
        ...,
        description="Follow-up question to ask about the video",
        examples=[
            "What topics do people discuss in the comments?",
            "Are there any controversial opinions?",
            "What do viewers like most about this video?"
        ]
    )


class DocumentMetadata(BaseModel):
    """Document metadata model."""

    type: str
    video_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    likes: Optional[int] = None
    published: Optional[str] = None


class RetrievedDocument(BaseModel):
    """Model for retrieved documents in responses."""

    content: str
    metadata: Dict[str, Any]


class StreamEvent(BaseModel):
    """Base model for streaming events."""

    type: str = Field(
        ...,
        description="Event type: progress, agent_message, final, error"
    )

    content: str = Field(
        ...,
        description="Event content/message"
    )


class AgentMessageEvent(StreamEvent):
    """Streaming event for agent messages."""

    type: Literal["agent_message"] = "agent_message"
    agent: str = Field(..., description="Agent name")


class ProgressEvent(StreamEvent):
    """Streaming event for progress updates."""

    type: Literal["progress"] = "progress"


class FinalResponseEvent(StreamEvent):
    """Streaming event for final response."""

    type: Literal["final"] = "final"
    documents: Optional[List[RetrievedDocument]] = Field(
        default=None,
        description="Retrieved documents used in response"
    )


class ErrorEvent(StreamEvent):
    """Streaming event for errors."""

    type: Literal["error"] = "error"


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
