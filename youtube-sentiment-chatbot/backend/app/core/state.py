"""State definitions for the multi-agent sentiment analysis system.

This module defines TypedDict states for:
- RAG graphs (basic retrieval-augmented generation)
- Research team graph (VideoSearch + CommentFinder)
- Analysis team graph (Sentiment + Topic)
- SuperSupervisor graph (meta-coordinator)

Memory Management:
- Uses LangGraph checkpointers to persist conversation state
- Thread-scoped memory maintains conversation history
- Supports follow-up questions in the same thread
"""

from typing import List, Annotated, Optional
from typing_extensions import TypedDict
import operator

from langchain_core.messages import BaseMessage
from langchain_core.documents import Document


class State(TypedDict):
    """Basic RAG state used for simple retrieval-augmented generation.

    Used in basic RAG graphs.

    Fields:
        question: User's query
        context: Retrieved documents
        response: Generated response
    """
    question: str
    context: List[Document]
    response: str


class ResearchTeamState(TypedDict):
    """State for the Research team graph.

    Manages conversation between VideoSearch and CommentFinder agents.

    Fields:
        messages: Conversation history (accumulated with operator.add)
        documents: Retrieved documents from CommentFinder
        team_members: List of agent names in the team
        next: Routing decision (agent name or "FINISH")
    """
    messages: Annotated[List[BaseMessage], operator.add]
    documents: List[Document]
    team_members: List[str]
    next: str


class SentimentState(TypedDict):
    """State for the Analysis team graph (also called AnalysisState).

    Manages conversation between Sentiment and Topic agents.

    Fields:
        messages: Conversation history (accumulated with operator.add)
        documents: Documents to analyze (from Research team)
        team_members: String of agent names in the team
        next: Routing decision (agent name or "FINISH")
    """
    messages: Annotated[List[BaseMessage], operator.add]
    documents: List[Document]
    team_members: str
    next: str


class SuperState(TypedDict):
    """Main state for the SuperSupervisor graph.

    Coordinates between Research team and Analysis team.

    Fields:
        messages: Overall conversation history (accumulated with operator.add)
        documents: Documents passed between teams
        next: Routing decision (team name or "FINISH")
    """
    messages: Annotated[List[BaseMessage], operator.add]
    documents: List[Document]
    next: str
