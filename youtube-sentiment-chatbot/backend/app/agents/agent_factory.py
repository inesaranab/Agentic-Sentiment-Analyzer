"""Agent factory functions for creating LangChain agents with LangGraph integration.

This module provides:
- Agent creation with OpenAI function calling
- Agent node wrappers for LangGraph integration
- Special document-preserving wrapper for CommentFinder agent
"""

from functools import partial
from typing import List

from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


# Autonomy enhancement text added to all agent system prompts
AUTONOMY_ENHANCEMENT = (
    "\nWork autonomously according to your specialty, using the tools available to you."
    " Do not ask for clarification."
    " Your other team members (and other teams) will collaborate with you with their own specialties."
    " You are chosen for a reason!"
)


def create_agent(
    llm: ChatOpenAI,
    tools: list,
    system_prompt: str,
) -> AgentExecutor:
    """Create a function-calling agent and add it to the graph.

    Args:
        llm: ChatOpenAI instance for the agent
        tools: List of tools the agent can use
        system_prompt: System instructions for the agent

    Returns:
        AgentExecutor configured with the agent and tools
    """
    system_prompt += AUTONOMY_ENHANCEMENT

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True)
    return executor


def agent_node(state, agent, name):
    """Standard agent execution wrapper for LangGraph.

    Args:
        state: Current graph state
        agent: AgentExecutor instance
        name: Name of the agent for message attribution

    Returns:
        Dictionary with messages and documents
    """
    result = agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["output"], name=name)],
        "documents": result.get("documents", [])
    }


def agent_node_with_docs(state, agent, name):
    """Special wrapper for CommentFinder agent that preserves documents.

    This function extracts documents from intermediate_steps because the
    retrieve_information tool returns a dict with both response and documents.

    Args:
        state: Current graph state
        agent: AgentExecutor instance
        name: Name of the agent for message attribution

    Returns:
        Dictionary with messages and preserved documents
    """
    result = agent.invoke(state)
    output = result["output"]

    # Try to extract documents if this is CommentFinder
    documents = []
    if name == "CommentFinder":
        # Parse the output to extract documents if they're returned
        # The tool returns a dict, but agent wraps it as string
        # We need to access the raw tool result
        try:
            # Get the intermediate steps from agent execution
            if "intermediate_steps" in result:
                for action, observation in result["intermediate_steps"]:
                    if isinstance(observation, dict) and "documents" in observation:
                        documents = observation["documents"]
        except Exception:
            documents = []

    return {
        "messages": [HumanMessage(content=output, name=name)],
        "documents": documents if documents else state.get("documents", [])
    }
