"""Main SuperSupervisor LangGraph.

This module builds the main meta-graph that coordinates:
- Research team (VideoSearch + CommentFinder)
- Analysis team (Sentiment + Topic)
- SuperSupervisor (routing between teams)

Memory Management:
- Uses MemorySaver checkpointer for conversation persistence
- Thread-scoped memory enables follow-up questions
- Maintains conversation history across multiple interactions
"""

from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state import SuperState
from app.core.prompts import SUPER_SUPERVISOR_PROMPT
from app.agents.supervisor import create_team_supervisor


def build_main_graph(
    super_llm,
    research_chain,
    analysis_chain
):
    """Build and compile the main SuperSupervisor graph with memory.

    The graph uses a MemorySaver checkpointer to persist conversation
    history within each thread. This enables:
    - Follow-up questions in the same conversation
    - Conversation state recovery across requests
    - Thread-scoped conversation isolation

    Args:
        super_llm: ChatOpenAI instance for super supervisor
        research_chain: Compiled research chain from build_research_graph
        analysis_chain: Compiled analysis chain from build_analysis_graph

    Returns:
        Compiled LangGraph with memory checkpointing
    """
    # Create Super Supervisor
    super_supervisor_agent = create_team_supervisor(
        super_llm,
        SUPER_SUPERVISOR_PROMPT,
        ["Research team", "Analysis team"]
    )

    # Helper functions
    def get_last_message(state: SuperState) -> str:
        """Extract content from last message in state."""
        return state["messages"][-1].content

    def join_graph(response: dict):
        """Format sub-graph response for parent graph."""
        result = {"messages": [response["messages"][-1]]}
        if "documents" in response and response["documents"]:
            result["documents"] = response["documents"]
        return result

    def get_messages_and_documents(state: SuperState):
        """Extract and pass data to analysis chain."""
        message = state["messages"][-1].content
        documents = state.get("documents", [])

        # Call analysis_chain with message and documents
        result = analysis_chain.invoke({"message": message, "documents": documents})

        return join_graph(result)

    # Build graph
    super_graph = StateGraph(SuperState)

    # Add nodes
    # Research team: get last message -> run research chain -> join result
    super_graph.add_node(
        "Research team",
        get_last_message | research_chain | join_graph
    )

    # Analysis team: get messages and documents -> run analysis chain
    super_graph.add_node(
        "Analysis team",
        get_messages_and_documents
    )

    # Super supervisor
    super_graph.add_node("SuperSupervisor", super_supervisor_agent)

    # Add edges (teams return to supervisor)
    super_graph.add_edge("Research team", "SuperSupervisor")
    super_graph.add_edge("Analysis team", "SuperSupervisor")

    # Add conditional edges from super supervisor
    super_graph.add_conditional_edges(
        "SuperSupervisor",
        lambda x: x["next"],
        {
            "Analysis team": "Analysis team",
            "Research team": "Research team",
            "FINISH": END
        }
    )

    # Set entry point
    super_graph.set_entry_point("SuperSupervisor")

    # Compile with MemorySaver checkpointer for conversation persistence
    checkpointer = MemorySaver()
    return super_graph.compile(checkpointer=checkpointer)
