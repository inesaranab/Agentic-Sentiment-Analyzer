"""Helper utility functions for the YouTube Sentiment Analyzer.

This module provides utility functions for:
- Extracting video IDs from YouTube URLs
- Formatting responses
- General helper utilities
"""

import re
from typing import Optional


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from a YouTube URL.

    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID

    Args:
        url: YouTube URL or video ID

    Returns:
        Extracted video ID or None if not found
    """
    # If it's already just a video ID (11 characters, alphanumeric + - and _)
    if re.match(r'^[A-Za-z0-9_-]{11}$', url):
        return url

    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([A-Za-z0-9_-]{11})',
        r'(?:youtu\.be\/)([A-Za-z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([A-Za-z0-9_-]{11})',
        r'(?:youtube\.com\/v\/)([A-Za-z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def format_agent_message(agent_name: str, content: str) -> dict:
    """Format agent message for streaming response.

    Args:
        agent_name: Name of the agent
        content: Message content

    Returns:
        Formatted message dictionary
    """
    return {
        "type": "agent_message",
        "agent": agent_name,
        "content": content
    }


def format_progress_message(content: str) -> dict:
    """Format progress message for streaming response.

    Args:
        content: Progress message content

    Returns:
        Formatted progress dictionary
    """
    return {
        "type": "progress",
        "content": content
    }


def format_final_response(content: str, documents: list = None) -> dict:
    """Format final response message.

    Args:
        content: Final response content
        documents: Optional list of relevant documents

    Returns:
        Formatted final response dictionary
    """
    response = {
        "type": "final",
        "content": content
    }

    if documents:
        response["documents"] = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in documents
        ]

    return response


def format_error_message(error: str) -> dict:
    """Format error message for streaming response.

    Args:
        error: Error message

    Returns:
        Formatted error dictionary
    """
    return {
        "type": "error",
        "content": error
    }
