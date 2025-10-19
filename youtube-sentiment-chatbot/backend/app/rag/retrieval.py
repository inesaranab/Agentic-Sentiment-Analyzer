"""BM25 retrieval implementation for RAG.

This module provides BM25-based keyword retrieval for:
- Video context chunks
- Individual comment documents
"""

from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever


class State(TypedDict):
    """State for RAG graph nodes."""
    question: str
    context: List[Document]
    response: str


def create_bm25_retriever(docs_for_store: List[Document]) -> BM25Retriever:
    """Create a BM25 retriever from prepared documents.

    Args:
        docs_for_store: Combined list of context chunks and comment documents

    Returns:
        Configured BM25Retriever instance
    """
    bm25_retriever = BM25Retriever.from_documents(docs_for_store)
    return bm25_retriever


def bm25_retrieve(state: State, bm25_retriever: BM25Retriever) -> dict:
    """Retrieve relevant documents using BM25 algorithm.

    Args:
        state: Current graph state with question
        bm25_retriever: Configured BM25 retriever instance

    Returns:
        Dictionary with retrieved context documents
    """
    retrieved_docs = bm25_retriever.invoke(state['question'])
    return {"context": retrieved_docs}


def make_bm25_retrieve(bm25_retriever: BM25Retriever):
    """Create a BM25 retrieve function bound to a specific retriever.

    This factory pattern is useful for LangGraph integration where you need
    a function that only takes state as input.

    Args:
        bm25_retriever: Configured BM25 retriever instance

    Returns:
        Retrieval function for use in LangGraph
    """
    def retrieve_fn(state: State) -> dict:
        retrieved_docs = bm25_retriever.invoke(state['question'])
        return {"context": retrieved_docs}

    return retrieve_fn
