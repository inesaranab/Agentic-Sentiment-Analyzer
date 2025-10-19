"""Document chunking and preparation for RAG.

This module handles:
- Chunking video context (transcript + metadata) using RecursiveCharacterTextSplitter
- Creating individual comment documents (no chunking)
- Combining both for BM25 retrieval
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# Chunking parameters (exported for consistency)
CHUNK_SIZE = 750
CHUNK_OVERLAP = 150


def prepare_documents_for_retrieval(
    unified_document: Document,
    formatted_comments: List[dict]
) -> tuple[Document, List[Document], List[Document]]:
    """Prepare documents for BM25 retrieval by creating context and comment documents.

    Args:
        unified_document: The unified video document with full content
        formatted_comments: List of formatted comment dictionaries

    Returns:
        Tuple of (context_doc, comment_docs, docs_for_store)
            - context_doc: Video-level document with full context
            - comment_docs: Individual documents per comment
            - docs_for_store: Combined chunks + comments for BM25 retriever
    """
    # Video-level context document
    context_doc = Document(
        page_content=unified_document.page_content,
        metadata={
            "type": "video_context",
            "video_id": unified_document.metadata["video_id"],
            "title": unified_document.metadata.get("title", ""),
            "channel": unified_document.metadata.get("channel", ""),
            "source": "youtube_unified",
        },
    )

    # One document per comment with rich payload
    comment_docs = [
        Document(
            page_content=comment["text"],
            metadata={
                "type": "comment",
                "comment_index": idx + 1,
                "author": comment["author"],
                "likes": comment["likes"],
                "published": comment["published"],
                "video_id": unified_document.metadata["video_id"],
                "title": unified_document.metadata.get("title", ""),
            },
        )
        for idx, comment in enumerate(formatted_comments)
    ]

    # Chunk the context document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    context_chunks = text_splitter.split_documents([context_doc])

    # CRITICAL: Combine context chunks + comment docs for BM25 retriever
    # No chunking for comments - they remain as individual documents
    docs_for_store = context_chunks + comment_docs

    return context_doc, comment_docs, docs_for_store
