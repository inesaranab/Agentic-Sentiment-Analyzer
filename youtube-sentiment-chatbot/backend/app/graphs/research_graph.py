"""Research Team LangGraph.

This module builds the Research Team graph that coordinates:
- VideoSearch agent (external web search with Tavily)
- CommentFinder agent (internal RAG retrieval)
- ResearchSupervisor (routing between agents)
"""

import functools
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

from app.core.state import ResearchTeamState
from app.core.prompts import (
    VIDEO_SEARCH_PROMPT,
    COMMENT_FINDER_PROMPT,
    RESEARCH_SUPERVISOR_PROMPT
)
from app.agents.agent_factory import create_agent, agent_node, agent_node_with_docs
from app.agents.supervisor import create_team_supervisor


def build_research_graph(
    research_llm,
    video_specific_search_tool,
    retrieve_information_tool
):
    """Build and compile the Research Team graph.

    Args:
        research_llm: ChatOpenAI instance for research agents
        video_specific_search_tool: Tool for Tavily search with video context
        retrieve_information_tool: Tool for RAG retrieval

    Returns:
        Compiled LangGraph for Research Team execution
    """
    # Create VideoSearch agent
    search_agent = create_agent(
        research_llm,
        [video_specific_search_tool],
        VIDEO_SEARCH_PROMPT
    )
    search_node = functools.partial(agent_node, agent=search_agent, name='VideoSearch')

    # Create CommentFinder agent (uses special wrapper to preserve documents)
    research_agent = create_agent(
        research_llm,
        [retrieve_information_tool],
        COMMENT_FINDER_PROMPT
    )
    research_node = functools.partial(agent_node_with_docs, agent=research_agent, name='CommentFinder')

    # Create Research Supervisor
    research_supervisor_agent = create_team_supervisor(
        research_llm,
        RESEARCH_SUPERVISOR_PROMPT,
        ["VideoSearch", "CommentFinder"]
    )

    # Build graph
    research_graph = StateGraph(ResearchTeamState)

    # Add nodes
    research_graph.add_node("VideoSearch", search_node)
    research_graph.add_node("CommentFinder", research_node)
    research_graph.add_node("ResearchSupervisor", research_supervisor_agent)

    # Add edges (workers return to supervisor)
    research_graph.add_edge("VideoSearch", "ResearchSupervisor")
    research_graph.add_edge("CommentFinder", "ResearchSupervisor")

    # Add conditional edges from supervisor
    research_graph.add_conditional_edges(
        "ResearchSupervisor",
        lambda x: x["next"],
        {"VideoSearch": "VideoSearch", "CommentFinder": "CommentFinder", "FINISH": END}
    )

    # Set entry point
    research_graph.set_entry_point("ResearchSupervisor")

    # Compile
    return research_graph.compile()


def create_research_chain(compiled_research_graph):
    """Create a research chain with helper functions for document preservation.

    Args:
        compiled_research_graph: Compiled Research Team graph

    Returns:
        Runnable chain for use in main graph
    """
    def enter_research_chain(message: str):
        """Format message for research chain entry."""
        return {
            "messages": [HumanMessage(content=message)],
        }

    def research_chain_with_docs(state):
        """Run research chain and preserve documents in state."""
        result = compiled_research_graph.invoke(state)

        # Explicitly extract and preserve documents
        return {
            "messages": result["messages"],
            "documents": result.get("documents", state.get("documents", []))
        }

    # Compose chain using RunnableLambda
    return (
        RunnableLambda(enter_research_chain)
        | RunnableLambda(research_chain_with_docs)
    )
