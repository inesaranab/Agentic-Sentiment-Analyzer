"""Unified video document builder.

This module creates a comprehensive LangChain Document containing all video context:
- Video metadata (title, channel, views, likes)
- Video transcript
- Comments with rich metadata (author, likes, published date)
"""

from langchain_core.documents import Document
from .collectors import get_youtube_comments, get_video_details, get_video_transcript


def create_unified_video_document(video_id: str, max_comments: int = 50):
    """Create a unified document containing video details, transcript, and comments.

    This gives the chatbot complete context about the video.

    Args:
        video_id: YouTube video ID
        max_comments: Maximum number of comments to retrieve (default: 50)

    Returns:
        Tuple of (unified_document, raw_blobs):
            - unified_document: LangChain Document with formatted content and metadata
            - raw_blobs: Dict containing raw API responses and formatted comments
    """
    # Get all data
    video_details = get_video_details(video_id)
    comments_data = get_youtube_comments(video_id, max_comments)
    transcript_data = get_video_transcript(video_id)

    # Extract key information
    video_info = video_details['items'][0] if video_details.get('items') else {}
    snippet = video_info.get('snippet', {})
    statistics = video_info.get('statistics', {})

    # Format comments
    formatted_comments = []
    if 'items' in comments_data:
        for item in comments_data['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            formatted_comments.append({
                'text': comment.get('textDisplay', ''),
                'author': comment.get('authorDisplayName', ''),
                'likes': comment.get('likeCount', 0),
                'published': comment.get('publishedAt', '')
            })

    # Create unified content
    unified_content = f"""
# VIDEO ANALYSIS CONTEXT

## Video Information
**Title:** {snippet.get('title', 'N/A')}
**Channel:** {snippet.get('channelTitle', 'N/A')}
**Published:** {snippet.get('publishedAt', 'N/A')}
**Views:** {statistics.get('viewCount', 'N/A')}
**Likes:** {statistics.get('likeCount', 'N/A')}
**Comments Count:** {statistics.get('commentCount', 'N/A')}

## Video Description
{snippet.get('description', 'No description available')}

## Video Transcript
{transcript_data.get('transcript', 'No transcription available')}

## Comments Analysis
**Total Comments Analyzed:** {len(formatted_comments)}

### Comment Details:
"""

    # Add individual comments
    for i, comment in enumerate(formatted_comments, 1):
        unified_content += f"""
**Comment {i}:**
- Author: {comment['author']}
- Likes: {comment['likes']}
- Published: {comment['published']}
- Text: {comment['text']}
---
"""

    # Create the document
    unified_document = Document(
        page_content=unified_content,
        metadata={
            "type": "unified_video_analysis",
            "video_id": video_id,
            "title": snippet.get('title', ''),
            "channel": snippet.get('channelTitle', ''),
            "comment_count": len(formatted_comments),
            "has_transcript": bool(transcript_data.get('transcript')),
            "views": statistics.get('viewCount', 0),
            "likes": statistics.get('likeCount', 0),
            "published": snippet.get('publishedAt', ''),
            "source": "youtube_unified"
        }
    )

    return unified_document, {
        'video_details': video_details,
        'comments': comments_data,
        'transcript': transcript_data,
        'formatted_comments': formatted_comments
    }
