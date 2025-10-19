"""YouTube data collection functions.

This module contains functions to fetch YouTube video data including:
- Comments with metadata (author, likes, published date)
- Video details (title, description, statistics)
- Video transcripts
"""

import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi


def get_youtube_comments(video_id: str, max_comments: int = 50):
    """Fetch comments from a YouTube video using YouTube Data API v3.

    Args:
        video_id: YouTube video ID
        max_comments: Maximum number of comments to retrieve (default: 50)

    Returns:
        JSON response with comment threads from YouTube API

    Requires:
        YOUTUBE_API_KEY environment variable
    """
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'maxResults': max_comments,
        'key': os.environ['YOUTUBE_API_KEY']
    }
    response = requests.get(url, params=params)
    return response.json()


def get_video_details(video_id: str):
    """Get video metadata including title, description, channel info, etc.

    Args:
        video_id: YouTube video ID

    Returns:
        JSON response with video snippet, statistics, and contentDetails

    Requires:
        YOUTUBE_API_KEY environment variable
    """
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,statistics,contentDetails',
        'id': video_id,
        'key': os.environ['YOUTUBE_API_KEY']
    }
    response = requests.get(url, params=params)
    return response.json()


def get_video_transcript(video_id: str):
    """Get video transcript using YouTube Transcript API.

    Args:
        video_id: YouTube video ID

    Returns:
        Dictionary with 'transcript' key containing concatenated text,
        or 'error' key if transcript fetch failed
    """
    try:
        api = YouTubeTranscriptApi()
        full_transcript = api.fetch(video_id)
        transcript_text = " ".join(
            full_transcript.snippets[i].text for i in range(len(full_transcript.snippets))
        )
        print(f"DEBUG: Transcript fetched for {video_id}, length={len(transcript_text)}")
        return {"transcript": transcript_text}

    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Transcript fetch failed for {video_id}: {exc}")
        return {
            "transcript": "",
            "error": f"Unable to fetch transcript: {exc}",
        }
