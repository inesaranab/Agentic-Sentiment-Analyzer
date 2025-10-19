"""API routes for YouTube Sentiment Analyzer.

This module provides endpoints for:
- Video analysis with streaming responses and memory persistence
- Follow-up questions within the same conversation thread
- Health check

Memory Management:
- Each video analysis creates a unique session (thread_id)
- Sessions persist conversation history and cached data
- Follow-up questions reuse the same graph and memory
"""

import json
import asyncio
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.api.models import (
    VideoAnalysisRequest,
    QueryRequest,
    HealthResponse
)
from app.core.configuration import default_config
from app.core.session_manager import session_manager
from app.utils.helpers import (
    extract_video_id,
    format_progress_message,
    format_final_response,
    format_error_message
)
from app.youtube.document_builder import create_unified_video_document
from app.rag.chunking import prepare_documents_for_retrieval
from app.rag.retrieval import create_bm25_retriever
from app.rag.generation import create_generator_llm
from app.graphs.rag_graph import build_rag_graph
from app.graphs.research_graph import build_research_graph, create_research_chain
from app.graphs.analysis_graph import build_analysis_graph, create_analysis_chain
from app.graphs.main_graph import build_main_graph
from app.agents.research_tools import (
    create_video_specific_search_tool,
    create_retrieve_information_tool
)


router = APIRouter()


async def analyze_video_stream(
    url: str,
    max_comments: int,
    question: str,
    session_id: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """Stream video analysis progress and results with conversation memory.

    This function handles both initial analyses and follow-up questions:
    - If session_id is None: Creates new session, builds full graph
    - If session_id provided: Reuses existing session with cached data

    Args:
        url: YouTube URL or video ID (required for new sessions)
        max_comments: Maximum number of comments to fetch
        question: Question to ask (initial or follow-up)
        session_id: Optional session ID for follow-up questions

    Yields:
        JSON-encoded streaming events including session_id
    """
    try:
        # Check if this is a follow-up question
        if session_id:
            yield json.dumps(format_progress_message(f"Continuing conversation in session: {session_id[:8]}...")) + "\n"
            
            session = session_manager.get_session(session_id)
            if not session or not session.main_graph:
                yield json.dumps(format_error_message("Session not found or expired. Please start a new analysis.")) + "\n"
                return
            
            yield json.dumps(format_progress_message(f"Using cached data for: {session.video_title}")) + "\n"
            
            # Use existing graph with memory
            main_graph = session.main_graph
            video_id = session.video_id
        else:
            # Step 1: Extract video ID for new session
            video_id = extract_video_id(url)
            if not video_id:
                yield json.dumps(format_error_message("Invalid YouTube URL or video ID")) + "\n"
                return

            yield json.dumps(format_progress_message(f"Analyzing video: {video_id}")) + "\n"

            # Step 2: Fetch YouTube data
            yield json.dumps(format_progress_message("Fetching video data, comments, and transcript...")) + "\n"

            unified_document, raw_blobs = create_unified_video_document(video_id, max_comments)

            title = unified_document.metadata.get("title", "Unknown")
            channel = unified_document.metadata.get("channel", "Unknown")

            yield json.dumps(format_progress_message(f"Video: {title} by {channel}")) + "\n"

            # Step 3: Create session
            new_session_id = session_manager.create_session(video_id, title, channel)
            session_id = new_session_id
            
            yield json.dumps({
                "type": "session_created",
                "session_id": session_id,
                "video_id": video_id,
                "title": title,
                "channel": channel
            }) + "\n"

            # Step 4: Prepare documents for BM25 retrieval
            yield json.dumps(format_progress_message("Preparing documents for retrieval...")) + "\n"

            context_doc, comment_docs, docs_for_store = prepare_documents_for_retrieval(
                unified_document,
                raw_blobs["formatted_comments"]
            )

            yield json.dumps(format_progress_message(
                f"Prepared {len(docs_for_store)} documents ({len(comment_docs)} comments)"
            )) + "\n"

            # Step 5: Build BM25 retriever and RAG graph
            yield json.dumps(format_progress_message("Building retrieval system...")) + "\n"

            bm25_retriever = create_bm25_retriever(docs_for_store)
            generator_llm = create_generator_llm(default_config.generator_model)

            compiled_rag_graph = build_rag_graph(bm25_retriever, generator_llm)

            # Step 6: Build multi-agent system with memory
            yield json.dumps(format_progress_message("Initializing multi-agent system with memory...")) + "\n"

            # Create LLMs for agents
            research_llm = ChatOpenAI(model=default_config.research_model)
            analysis_llm = ChatOpenAI(model=default_config.analysis_model)
            super_llm = ChatOpenAI(model=default_config.supervisor_model)

            # Create tools
            transcript = raw_blobs["transcript"].get("transcript", "")
            video_specific_search_tool = create_video_specific_search_tool(title, channel, transcript)
            retrieve_information_tool = create_retrieve_information_tool(compiled_rag_graph)

            # Build graphs
            compiled_research_graph = build_research_graph(
                research_llm,
                video_specific_search_tool,
                retrieve_information_tool
            )

            compiled_analysis_graph = build_analysis_graph(analysis_llm)

            # Create chains
            research_chain = create_research_chain(compiled_research_graph)
            analysis_chain = create_analysis_chain(compiled_analysis_graph)

            # Build main graph with memory checkpointer
            main_graph = build_main_graph(super_llm, research_chain, analysis_chain)
            
            # Update session with artifacts
            session_manager.update_session(
                session_id,
                main_graph=main_graph,
                documents=docs_for_store,
                bm25_retriever=bm25_retriever,
                raw_blobs=raw_blobs
            )

        # Step 7: Stream graph execution with thread_id for memory
        yield json.dumps(format_progress_message("Starting analysis...")) + "\n"

        initial_state = {
            "messages": [HumanMessage(content=question)]
        }

        # Use thread_id (session_id) for conversation memory
        config = {"configurable": {"thread_id": session_id}}

        # Execute graph with streaming
        async for event in main_graph.astream(
            initial_state,
            config
        ):
            # Skip end event
            if "__end__" in event:
                continue

            # Extract node name and state
            for node_name, state_update in event.items():
                # Yield progress for each node execution
                if "messages" in state_update and state_update["messages"]:
                    last_message = state_update["messages"][-1]

                    # Extract agent name from message
                    agent_name = getattr(last_message, "name", node_name)
                    content = last_message.content

                    yield json.dumps({
                        "type": "agent_message",
                        "agent": agent_name,
                        "content": content,
                        "session_id": session_id,
                        "metadata": {
                            "agent_name": agent_name,
                            "langgraph_node": node_name
                        }
                    }) + "\n"

        # Step 8: Get final state and format response
        final_state = await main_graph.ainvoke(
            initial_state,
            config
        )

        if final_state and "messages" in final_state and final_state["messages"]:
            final_content = final_state["messages"][-1].content
            final_documents = final_state.get("documents", [])

            response = format_final_response(final_content, final_documents)
            response["session_id"] = session_id
            yield json.dumps(response) + "\n"
        else:
            yield json.dumps(format_error_message("No response generated")) + "\n"

    except Exception as e:
        yield json.dumps(format_error_message(f"Error during analysis: {str(e)}")) + "\n"


@router.post("/analyze")
async def analyze_video(request: VideoAnalysisRequest):
    """Analyze a YouTube video and return streaming results with session memory.

    This endpoint:
    1. Fetches video data, comments, and transcript
    2. Prepares documents for BM25 retrieval
    3. Builds multi-agent system with memory checkpointer
    4. Creates a unique session ID (thread_id) for conversation
    5. Streams analysis progress and results

    The returned session_id can be used for follow-up questions
    via the /query endpoint.

    Args:
        request: Video analysis request with URL and parameters

    Returns:
        StreamingResponse with JSON events including session_id
    """
    return StreamingResponse(
        analyze_video_stream(
            request.url,
            request.max_comments,
            request.question or "What is the overall sentiment of the comments on this video?",
            None  # New session
        ),
        media_type="text/event-stream"
    )


@router.post("/query")
async def query_video(request: QueryRequest):
    """Ask a follow-up question within an existing conversation thread.

    This endpoint reuses the cached video data and multi-agent system
    from a previous analysis, maintaining conversation history through
    the session's thread_id.

    Benefits of follow-up questions:
    - No need to re-analyze the video
    - Conversation context is preserved
    - Much faster response time
    - Can ask multiple related questions

    Args:
        request: Query request with session_id and question

    Returns:
        StreamingResponse with JSON events
    """
    if not request.session_id:
        raise HTTPException(
            status_code=400,
            detail="session_id is required for follow-up questions"
        )
    
    return StreamingResponse(
        analyze_video_stream(
            "",  # URL not needed for follow-up
            50,  # max_comments not needed for follow-up
            request.question,
            request.session_id  # Existing session
        ),
        media_type="text/event-stream"
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.

    Returns:
        Health status and version
    """
    return HealthResponse(status="healthy", version="1.0.0")
