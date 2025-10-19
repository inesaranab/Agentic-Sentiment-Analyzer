"""Research Tools for Multi-Agent Sentiment Analyzer.

This module provides:
- video_specific_search: Tavily search enhanced with video context
- retrieve_information: RAG retrieval returning response + documents
"""

from typing import Annotated, List
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch


# Global state for document preservation (set by retrieve_information tool)
_retrieved_documents = []

# Tavily search instance
tavily = TavilySearch(max_results=5)

# Summarization chain for transcript compression
SUMMARIZATION_TEMPLATE = (
    "You are an editorial analyst turning raw YouTube transcripts into concise research briefings.\n"
    "Video title: {title}\n"
    "Channel: {channel}\n"
    "Transcript excerpt:\n{transcript}\n\n"
    "Write a tight summary under 110 words that:"
    "\n- Captures the main topics and arguments"
    "\n- Names key people, brands, or entities mentioned"
    "\n- Notes tone shifts or controversies if present"
    "\n- Highlights any actionable insights for a researcher"
    "\nUse short sentences separated by semicolons. If the transcript excerpt is empty, respond with 'No transcript available.'"
)

summarization_llm = ChatOpenAI(model='gpt-4o-mini')
chat_summarization_prompt = ChatPromptTemplate.from_messages([("human", SUMMARIZATION_TEMPLATE)])
summarization_chain = chat_summarization_prompt | summarization_llm | StrOutputParser()


def create_video_specific_search_tool(title: str, channel: str, transcript: str):
    """Create a video_specific_search tool bound to video context.

    Args:
        title: Video title
        channel: Channel name
        transcript: Full video transcript

    Returns:
        Tool function for Tavily search enhanced with video context
    """
    @tool
    def video_specific_search(
        query: Annotated[str, "Search query - can be about the current video's topic OR to find other related videos"]
    ) -> str:
        """Search for external information using web search (Tavily).

        Use this for:
        - Finding other videos from the same creator/channel
        - Searching for information about topics mentioned in the video
        - Looking up external context related to the video's content
        - General web searches enhanced with video context

        The search automatically includes the current video's title and channel for context.
        """
        search_context: List[str] = []
        if title:
            search_context.append(f'"{title}"')
        if channel:
            search_context.append(f"channel:{channel}")
        if transcript:
            summary = summarization_chain.invoke(
                {
                    "title": title,
                    "channel": channel,
                    "transcript": transcript,
                }
            )
            search_context.append(f"transcript summary: {summary}")

        enhanced_query = f"{query} {' '.join(search_context)}" if search_context else query

        # Tavily can return different formats - handle all cases
        results = tavily.invoke(enhanced_query)

        output_lines = [f"## Search Results for: {title or 'Unknown Video'}"]
        output_lines.append(f"**Channel:** {channel or 'Unknown Channel'}")
        output_lines.append(f"**Enhanced Query:** {enhanced_query}\n")
        
        # Handle different return types from Tavily
        if isinstance(results, str):
            # If it's already a formatted string
            output_lines.append("### Search Results")
            output_lines.append(results)
        elif isinstance(results, list):
            # If it's a list of results
            for index, result in enumerate(results[:4], start=1):
                output_lines.append(f"### Result {index}")
                if isinstance(result, dict):
                    output_lines.append(f"**URL:** {result.get('url', 'N/A')}")
                    output_lines.append(f"**Title:** {result.get('title', 'N/A')}")
                    output_lines.append(f"**Summary:** {result.get('content', 'No content available')}")
                else:
                    output_lines.append(f"**Content:** {str(result)}")
        elif isinstance(results, dict):
            # If it's a single result dict
            output_lines.append("### Search Result")
            output_lines.append(f"**URL:** {results.get('url', 'N/A')}")
            output_lines.append(f"**Title:** {results.get('title', 'N/A')}")
            output_lines.append(f"**Content:** {results.get('content', 'No content available')}")
        else:
            # Fallback for unknown format
            output_lines.append(f"**Results:** {str(results)}")

        return "\n".join(output_lines)

    return video_specific_search


def create_retrieve_information_tool(compiled_rag_graph):
    """Create a retrieve_information tool bound to a RAG graph.

    Args:
        compiled_rag_graph: Compiled LangGraph for RAG retrieval

    Returns:
        Tool function for RAG retrieval
    """
    @tool
    def retrieve_information(
        query: Annotated[str, "query to ask the retrieve information tool"]
    ):
        """Use Retrieval Augmented Generation to retrieve information related to user query."""
        global _retrieved_documents

        result = compiled_rag_graph.invoke({"question": query})

        _retrieved_documents = result['context']

        # Also return dict (though tool will serialize it to string)
        return {
            "response": result['response'],
            "documents": result['context']
        }

    return retrieve_information


def get_retrieved_documents():
    """Get documents retrieved by the last retrieve_information call.

    Returns:
        List of retrieved documents
    """
    return _retrieved_documents
