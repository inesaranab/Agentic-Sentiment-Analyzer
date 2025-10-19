"""Analysis Team LangGraph.

This module builds the Analysis Team graph that coordinates:
- Sentiment agent (sentiment analysis with reflection)
- Topic agent (topic extraction with reflection)
- AnalysisSupervisor (routing between agents)
"""

import functools
from typing import List
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

from app.core.state import SentimentState
from app.core.prompts import (
    SENTIMENT_AGENT_PROMPT,
    TOPIC_AGENT_PROMPT,
    ANALYSIS_SUPERVISOR_PROMPT
)
from app.agents.agent_factory import create_agent, agent_node
from app.agents.supervisor import create_team_supervisor
from app.agents.analysis_tools import sentiment_think_tool, topic_think_tool


def build_analysis_graph(analysis_llm):
    """Build and compile the Analysis Team graph.

    Args:
        analysis_llm: ChatOpenAI instance for analysis agents

    Returns:
        Compiled LangGraph for Analysis Team execution
    """
    # Create Topic agent
    topic_agent = create_agent(
        analysis_llm,
        [topic_think_tool],
        TOPIC_AGENT_PROMPT
    )
    topic_node = functools.partial(agent_node, agent=topic_agent, name='Topic')

    # Create Sentiment agent
    sentiment_agent = create_agent(
        analysis_llm,
        [sentiment_think_tool],
        SENTIMENT_AGENT_PROMPT
    )
    sentiment_node = functools.partial(agent_node, agent=sentiment_agent, name='Sentiment')

    # Create Analysis Supervisor
    analysis_supervisor_agent = create_team_supervisor(
        analysis_llm,
        ANALYSIS_SUPERVISOR_PROMPT,
        ["Topic", "Sentiment"]
    )

    # Build graph
    sentiment_graph = StateGraph(SentimentState)

    # Add nodes
    sentiment_graph.add_node("Topic", topic_node)
    sentiment_graph.add_node("Sentiment", sentiment_node)
    sentiment_graph.add_node("AnalysisSupervisor", analysis_supervisor_agent)

    # Add edges (workers return to supervisor)
    sentiment_graph.add_edge("Topic", "AnalysisSupervisor")
    sentiment_graph.add_edge("Sentiment", "AnalysisSupervisor")

    # Add conditional edges from supervisor
    sentiment_graph.add_conditional_edges(
        "AnalysisSupervisor",
        lambda x: x["next"],
        {
            "Topic": "Topic",
            "Sentiment": "Sentiment",
            "FINISH": END
        }
    )

    # Set entry point
    sentiment_graph.set_entry_point("AnalysisSupervisor")

    # Compile
    return sentiment_graph.compile()


def create_analysis_chain(compiled_sentiment_graph):
    """Create an analysis chain with helper functions for state preparation.

    Args:
        compiled_sentiment_graph: Compiled Analysis Team graph

    Returns:
        Runnable chain for use in main graph
    """
    # Get member names from compiled graph nodes
    members = ["Topic", "Sentiment"]

    def enter_sentiment_chain(state: dict):
        """Prepare state for sentiment analysis team."""
        return {
            "messages": [HumanMessage(content=state["message"])],
            "documents": state.get("documents", []),
            "team_members": ", ".join(members)
        }

    # Compose chain using RunnableLambda
    return (
        RunnableLambda(enter_sentiment_chain)
        | compiled_sentiment_graph
    )
