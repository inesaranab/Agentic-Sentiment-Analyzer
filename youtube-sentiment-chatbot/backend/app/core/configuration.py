"""Configuration management for the YouTube Sentiment Analyzer.

This module provides configuration for:
- LLM models and parameters
- API keys and environment variables
- System-wide settings
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LLMModel(Enum):
    """Available LLM models."""
    GPT_4_NANO = "gpt-4.1-nano"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


class Configuration(BaseModel):
    """Main configuration class for the YouTube Sentiment Analyzer."""

    # LLM Configuration
    generator_model: str = Field(
        default=LLMModel.GPT_4_NANO.value,
        description="Model for RAG response generation"
    )

    research_model: str = Field(
        default=LLMModel.GPT_4O_MINI.value,
        description="Model for research agents"
    )

    analysis_model: str = Field(
        default=LLMModel.GPT_4O_MINI.value,
        description="Model for analysis agents"
    )

    supervisor_model: str = Field(
        default=LLMModel.GPT_4O_MINI.value,
        description="Model for supervisors"
    )

    summarization_model: str = Field(
        default=LLMModel.GPT_4O_MINI.value,
        description="Model for transcript summarization"
    )

    # YouTube Configuration
    max_comments: int = Field(
        default=50,
        description="Maximum number of comments to fetch from YouTube"
    )

    # RAG Configuration
    chunk_size: int = Field(
        default=750,
        description="Chunk size for RecursiveCharacterTextSplitter"
    )

    chunk_overlap: int = Field(
        default=150,
        description="Chunk overlap for RecursiveCharacterTextSplitter"
    )

    # Graph Configuration
    max_iterations: int = Field(
        default=100,
        description="Maximum recursion limit for LangGraph execution"
    )

    # API Keys (loaded from environment)
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="OpenAI API key"
    )

    youtube_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("YOUTUBE_API_KEY"),
        description="YouTube Data API key"
    )

    tavily_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY"),
        description="Tavily Search API key"
    )

    langchain_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGCHAIN_API_KEY"),
        description="LangChain API key for tracing"
    )

    class Config:
        """Pydantic config."""
        use_enum_values = True


# Default configuration instance
default_config = Configuration()
