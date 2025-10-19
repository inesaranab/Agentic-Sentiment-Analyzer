"""Supervisor functions for creating LLM-based routing supervisors in LangGraph.

This module provides:
- Team supervisor creation with OpenAI function calling
- Route function binding for supervisor decision-making
"""

from typing import List

from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from app.core.prompts import SUPERVISOR_ROUTING_QUESTION




def create_team_supervisor(llm: ChatOpenAI, system_prompt: str, members: List[str]):
    """Create an LLM-based router/supervisor for agent teams.

    The supervisor uses OpenAI function calling to decide which team member
    should act next, or if the task is complete (FINISH).

    Args:
        llm: ChatOpenAI instance for the supervisor
        system_prompt: System instructions for the supervisor
        members: List of team member names

    Returns:
        Runnable chain that returns routing decision
    """
    options = ["FINISH"] + members

    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                },
            },
            "required": ["next"],
        },
    }

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
               SUPERVISOR_ROUTING_QUESTION
            ),
        ]
    ).partial(options=str(options), team_members=", ".join(members))

    # JsonOutputToolsParser returns list of dicts like [{"type": "route", "args": {"next": "AgentName"}}]
    # We need to extract the "next" value from the first tool call
    def extract_next(output):
        """Extract the 'next' field from tool parser output."""
        if isinstance(output, list) and len(output) > 0:
            return output[0].get("args", {})
        return output

    return (
        prompt
        | llm.bind_tools(tools=[function_def], tool_choice={"type": "function", "function": {"name": "route"}})
        | JsonOutputToolsParser()
        | RunnableLambda(extract_next)
    )
