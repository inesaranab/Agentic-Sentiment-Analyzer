"""RAG graph for BM25 retrieval and LLM generation.

This module builds a simple RAG graph:
1. Retrieve relevant documents using BM25
2. Generate response using LLM with retrieved context
"""

from langgraph.graph import StateGraph, START, END

from app.core.state import State
from app.rag.retrieval import make_bm25_retrieve
from app.rag.generation import make_generate


def build_rag_graph(bm25_retriever, generator_llm):
    """Build and compile the BM25 RAG graph.

    Args:
        bm25_retriever: BM25Retriever instance
        generator_llm: ChatOpenAI instance for generation

    Returns:
        Compiled LangGraph for RAG execution
    """
    # Create bound functions
    retrieve_fn = make_bm25_retrieve(bm25_retriever)
    generate_fn = make_generate(generator_llm)

    # Build graph
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("retrieve", retrieve_fn)
    graph.add_node("generate", generate_fn)

    # Add edges
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    # Compile and return
    return graph.compile()
