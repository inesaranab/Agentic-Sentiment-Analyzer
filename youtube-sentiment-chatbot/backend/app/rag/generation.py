"""LLM generation for RAG responses.

This module provides LLM-based response generation using:
- Retrieved context (comments + video chunks)
- User question
- Structured prompt template
"""

from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


class State(TypedDict):
    """State for RAG graph nodes."""
    question: str
    context: List[Document]
    response: str


# Chat prompt template for generation
HUMAN_TEMPLATE = """
#CONTEXT:
{context}

QUERY:
{query}

"Use the provided context, which consists of YouTube comments, "
"to answer the user query. Only use the provided context to answer the query."
"When forming your response, take into account the topics discussed, the users who made the comments, "
"and the sentiment expressed in the comments to increase factual correctness and answer relevancy. "
"The chatbot is intended to answer questions about users' opinions of the video. "
"If you do not know the answer, or it is not contained in the provided context, respond with "I don't know.""
"""

chat_prompt = ChatPromptTemplate.from_messages([
    ("human", HUMAN_TEMPLATE)
])


def create_generator_llm(model: str = "gpt-4.1-nano") -> ChatOpenAI:
    """Create a ChatOpenAI instance for generation.

    Args:
        model: Model name to use (default: gpt-4.1-nano)

    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(model=model)


def generate(state: State, generator_llm: ChatOpenAI, prompt: ChatPromptTemplate = chat_prompt) -> dict:
    """Generate response using LLM based on retrieved context.

    Args:
        state: Current graph state with question and context
        generator_llm: ChatOpenAI model instance
        prompt: Chat prompt template (default: chat_prompt)

    Returns:
        Dictionary with generated response
    """
    generator_chain = prompt | generator_llm | StrOutputParser()
    response = generator_chain.invoke({
        "query": state['question'],
        "context": state["context"]
    })
    return {'response': response}


def make_generate(generator_llm: ChatOpenAI, prompt: ChatPromptTemplate = chat_prompt):
    """Create a generate function bound to a specific LLM and prompt.

    This factory pattern is useful for LangGraph integration where you need
    a function that only takes state as input.

    Args:
        generator_llm: ChatOpenAI model instance
        prompt: Chat prompt template (default: chat_prompt)

    Returns:
        Generation function for use in LangGraph
    """
    def generate_fn(state: State) -> dict:
        generator_chain = prompt | generator_llm | StrOutputParser()
        response = generator_chain.invoke({
            "query": state['question'],
            "context": state["context"]
        })
        return {'response': response}

    return generate_fn
