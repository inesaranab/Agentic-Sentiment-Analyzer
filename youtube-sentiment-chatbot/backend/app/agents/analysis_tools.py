"""Analysis Tools for Multi-Agent Sentiment Analyzer.

This module provides reflection tools for:
- Sentiment analysis quality assurance
- Topic extraction quality assurance
"""

from typing import Annotated
from langchain_core.tools import tool


@tool(description="Sentiment analysis reflection tool for quality decision-making")
def sentiment_think_tool(reflection: str) -> str:
    """Tool for strategic reflection during sentiment analysis workflows.

    Use this tool to pause and reflect on sentiment analysis progress, ensuring high-quality insights.

    When to use:
    - After processing comment batches: What sentiment patterns emerged?
    - Before finalizing analysis: Do I have sufficient data for reliable conclusions?
    - When encountering mixed sentiments: How should I categorize ambiguous cases?
    - Before generating reports: Are my sentiment classifications well-supported?

    Reflection should address:
    1. Sentiment pattern recognition - What dominant sentiments did I identify?
    2. Data quality assessment - Are the comments representative and sufficient?
    3. Classification confidence - How certain am I about sentiment labels?
    4. Analysis completeness - Do I need more data or can I proceed with conclusions?

    Args:
        reflection: Your detailed reflection on sentiment analysis findings, patterns, and next steps

    Returns:
        Confirmation that sentiment analysis reflection was recorded
    """
    return f"Sentiment analysis reflection recorded: {reflection}"


@tool(description="Topic extraction reflection tool for quality categorization")
def topic_think_tool(reflection: str) -> str:
    """Tool for strategic reflection during topic extraction workflows.

    Use this tool to pause and reflect on topic discovery progress, ensuring comprehensive theme identification.

    When to use:
    - After processing content batches: What topics and themes emerged?
    - Before finalizing categorization: Do I have sufficient examples for each topic?
    - When encountering ambiguous content: How should I categorize unclear topics?
    - Before generating topic reports: Are my topic classifications well-supported?

    Reflection should address:
    1. Topic discovery - What distinct themes and subjects did I identify?
    2. Topic coverage - Do I have enough examples for reliable topic classification?
    3. Classification confidence - How certain am I about topic labels and boundaries?
    4. Analysis completeness - Do I need more content or can I proceed with topic conclusions?

    Args:
        reflection: Your detailed reflection on topic extraction findings, themes, and next steps

    Returns:
        Confirmation that topic extraction reflection was recorded
    """
    return f"Topic extraction reflection recorded: {reflection}"

@tool(description="Strategic reflection tool for routing plan with dependency analysis")
def supervisor_think_tool(reflection: str) -> str:
    """Tool for strategic reflection on progress, decision-making, and DEPENDENCY CHECKING.

    Use this tool BEFORE routing to any agent to ensure all prerequisites are met.
    This creates a deliberate pause for quality decision-making and proper task sequencing.

    CRITICAL - DEPENDENCY CHECKING (Check BEFORE routing):
    
    Questions about SENTIMENT or EMOTIONAL TONE:
    → REQUIRES: Comments from CommentFinder agent FIRST
    → Sequence: CommentFinder → Sentiment Agent
    → Examples: "What's the sentiment?", "How do people feel?", "Are comments positive?"
    
    Questions about TOPICS or THEMES:
    → REQUIRES: Comments from CommentFinder agent FIRST  
    → Sequence: CommentFinder → Topic Analysis Agent
    → Examples: "What topics are discussed?", "Main themes?", "What do comments talk about?"
    
    Questions about SPECIFIC COMMENTS or COMMENT CONTENT:
    → REQUIRES: Comments from CommentFinder agent FIRST
    → Sequence: CommentFinder → (optional) Analysis Agent
    → Examples: "Show me comments about X", "What do comments say about Y?"
    
    Questions about VIDEO CONTEXT (not comment-specific):
    → Can route directly to VideoSearch agent
    → Examples: "What is this video about?", "Who is the creator?", "Related videos?"
    
    GENERAL QUESTIONS combining multiple aspects:
    → Determine ALL required agents and dependencies
    → Create execution sequence ensuring prerequisites run first
    → Example: "Sentiment + Topics" → CommentFinder → Sentiment + Topic (parallel)

    When to use this tool:
    - BEFORE routing any user query (mandatory dependency check)
    - After receiving agent results: What did I learn? What's next?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding: Can I provide a complete answer now?

    Reflection should address:
    1. DEPENDENCY CHECK - Does the target agent need data from another agent first?
    2. EXECUTION PLAN - What's the correct sequence? (e.g., [CommentFinder → Sentiment])
    3. Analysis of current findings - What concrete information have I gathered?
    4. Gap assessment - What crucial information is still missing?
    5. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    6. Strategic decision - Continue to next agent or provide final answer?

    Args:
        reflection: Your detailed reflection on dependencies, routing plan, progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Strategic reflection recorded: {reflection}"
