# YouTube Sentiment Analyzer - Migration Plan
## Step 1: Notebook Function Inventory & Module Mapping

**Date:** October 19, 2025  
**Goal:** Migrate `multi_agent_sentiment_analyzer.ipynb` logic into production-ready functional modules following `10_Open_DeepResearch/open_deep_library` structure

---

## 📋 Complete Function Inventory

### 1. **Data Collection Functions** (`app/services/youtube.py`)

#### Core YouTube API Functions
| Function | Purpose | Dependencies | Preserve |
|----------|---------|--------------|----------|
| `get_youtube_comments(video_id, max_comments)` | Fetch comments via YouTube API | requests, os.environ | ✅ CRITICAL |
| `get_video_details(video_id)` | Fetch video metadata | requests, os.environ | ✅ CRITICAL |
| `get_video_transcript(video_id)` | Fetch transcript via YouTube Transcript API | YouTubeTranscriptApi | ✅ CRITICAL |

**Notes:**
- All three functions are the **foundation** of the system
- Must preserve exact API call structure
- Error handling in `get_video_transcript` is intentional (handles missing transcripts gracefully)

---

### 2. **Document Building Functions** (`app/services/documents.py`)

#### Document Construction
| Function | Purpose | Dependencies | Preserve |
|----------|---------|--------------|----------|
| `create_unified_video_document(video_id, max_comments)` | Create unified document with all video data | Document, previous 3 functions | ✅ CRITICAL |

**Key Outputs:**
1. `unified_document` - Single Document with all context (video info + transcript + comments)
2. `raw_blobs` - Dict containing:
   - `video_details`
   - `comments`
   - `transcript`
   - `formatted_comments` (list of dicts with `text`, `author`, `likes`, `published`)

**Document Structure Creation** (inline notebook code):
```python
# Context document
context_doc = Document(
    page_content=unified_document.page_content,
    metadata={...}
)

# Comment documents (one per comment)
comment_docs = [Document(...) for comment in formatted_comments]
```

**Notes:**
- The formatted_comments structure is used by multiple agents
- Metadata fields are critical for filtering/searching
- Must preserve the exact metadata schema

---

### 3. **Retrieval Pipeline Functions** (`app/retrieval/`)

#### Document Chunking & Storage (`app/retrieval/chunking.py`)
| Component | Purpose | Configuration | Preserve |
|-----------|---------|---------------|----------|
| `RecursiveCharacterTextSplitter` | Chunk long context (transcripts) | chunk_size=750, chunk_overlap=150 | ✅ CRITICAL |
| `docs_for_store` construction | Combine chunks + comments | context_chunks + comment_docs | ✅ CRITICAL |

#### Embedding & Vector Store (`app/retrieval/vector_store.py`)
| Component | Purpose | Configuration | Preserve |
|-----------|---------|---------------|----------|
| `OpenAIEmbeddings` | Embed documents | model="text-embedding-3-small" | ✅ CRITICAL |
| `QdrantVectorStore` | Store vectors | collection="video_sentiment_data", Distance.COSINE, size=1536 | ✅ CRITICAL |
| `qdrant_retriever` | Retrieve similar docs | search_kwargs={"k": 6} | ✅ CRITICAL |

#### Alternative Retrievers (`app/retrieval/advanced.py`)
| Component | Purpose | Configuration | Preserve |
|-----------|---------|---------------|----------|
| `CohereRerank` | Rerank with compression | model="rerank-v3.5", top_n=4 | ✅ For evaluation |
| `ContextualCompressionRetriever` | Compression wrapper | Uses Cohere | ✅ For evaluation |
| `MultiQueryRetriever` | Multi-query expansion | Uses generator_llm | ✅ For evaluation |
| `BM25Retriever` | Keyword-based retrieval | From docs_for_store | ✅ For evaluation |

---

### 4. **Prompts** (`app/prompts/`)

#### RAG Prompts (`app/prompts/rag.py`)
| Prompt | Purpose | Preserve |
|--------|---------|----------|
| `HUMAN_TEMPLATE` | Main RAG prompt for context + query | ✅ CRITICAL - exact wording matters |
| `chat_prompt` | ChatPromptTemplate wrapper | ✅ CRITICAL |

#### Summarization Prompts (`app/prompts/research.py`)
| Prompt | Purpose | Preserve |
|--------|---------|----------|
| `SUMMARIZATION_TEMPLATE` | Summarize transcript for search enhancement | ✅ CRITICAL |
| `chat_summarization_prompt` | Wrapper for summarization | ✅ CRITICAL |

---

### 5. **LLM Configurations** (`app/llms/`)

| LLM Instance | Model | Purpose | Preserve |
|--------------|-------|---------|----------|
| `generator_llm` | gpt-4.1-nano | Generation in RAG | ✅ CRITICAL |
| `research_llm` | gpt-4o-mini | Research team agents | ✅ CRITICAL |
| `analysis_llm` | gpt-4o-mini | Analysis team agents | ✅ CRITICAL |
| `super_llm` | gpt-4o-mini | Meta-supervisor | ✅ CRITICAL |
| `summarization_llm` | gpt-4o-mini | Transcript summarization | ✅ CRITICAL |
| `evaluator_llm` | gpt-4o | RAGAS evaluation | ✅ For eval only |

**Notes:**
- Model choices are deliberate (nano for generation, mini for reasoning)
- Must preserve exact model names

---

### 6. **Agent Helper Functions** (`app/agents/`)

#### Core Agent Functions (`app/agents/helpers.py`)
| Function | Purpose | Signature | Preserve |
|----------|---------|-----------|----------|
| `agent_node(state, agent, name)` | Standard agent node wrapper | Returns {messages, documents} | ✅ CRITICAL |
| `agent_node_with_docs(state, agent, name)` | Special wrapper for CommentFinder | Extracts intermediate_steps for documents | ✅ CRITICAL |
| `create_agent(llm, tools, system_prompt)` | Create function-calling agent | Returns AgentExecutor | ✅ CRITICAL |
| `create_team_supervisor(llm, system_prompt, members)` | Create routing supervisor | Returns runnable chain | ✅ CRITICAL |

**Notes:**
- `agent_node_with_docs` handles special document extraction for CommentFinder
- System prompts get auto-enhanced with team collaboration instructions
- Supervisor uses function calling with "route" function

---

### 7. **Tools** (`app/tools/`)

#### Research Tools (`app/tools/search.py`)
| Tool | Purpose | Dependencies | Preserve |
|------|---------|--------------|----------|
| `video_specific_search` | Web search enhanced with video context | TavilySearch, summarization_chain | ✅ CRITICAL |

**Tool Configuration:**
```python
@tool
def video_specific_search(query: str) -> str:
    # Uses: title, channel, transcript, summarization_chain
    # Returns: Formatted search results with URLs
```

**Global Context Requirements:**
- `title` - from unified_document.metadata
- `channel` - from unified_document.metadata  
- `transcript` - from unified_document.page_content
- `formatted_comments` - from raw_blobs

#### Retrieval Tools (`app/tools/retrieval.py`)
| Tool | Purpose | Dependencies | Preserve |
|------|---------|--------------|----------|
| `retrieve_information` | RAG-based retrieval | compiled_rag_graph | ✅ CRITICAL |

**Special Behavior:**
- Uses global `_retrieved_documents` list to store results
- Returns dict with `response` and `documents`
- **IMPORTANT:** This pattern needs refactoring for production (no globals)

#### Analysis Tools (`app/tools/analysis.py`)
| Tool | Purpose | Description | Preserve |
|------|---------|-------------|----------|
| `sentiment_think_tool` | Sentiment analysis reflection | Guides agent thinking process | ✅ CRITICAL |
| `topic_think_tool` | Topic extraction reflection | Guides agent thinking process | ✅ CRITICAL |

**Notes:**
- These are "thinking" tools - they don't do computation, they guide agent reflection
- Return confirmation messages only
- Descriptions are very detailed and intentional

---

### 8. **LangGraph Workflows** (`app/graphs/`)

#### Baseline RAG Graph (`app/graphs/baseline_rag.py`)
| Component | Type | Purpose | Preserve |
|-----------|------|---------|----------|
| `State` TypedDict | Schema | {question, context, response} | ✅ CRITICAL |
| `retrieve(state)` | Node function | Calls qdrant_retriever | ✅ CRITICAL |
| `generate(state)` | Node function | Calls chat_prompt + generator_llm | ✅ CRITICAL |
| `rag_graph` | StateGraph | Links retrieve -> generate | ✅ CRITICAL |
| `compiled_rag_graph` | CompiledGraph | Executable graph | ✅ CRITICAL |

**Alternative RAG Graphs (for evaluation):**
- `compiled_advanced_rag_graph` - uses compression_retriever
- `compiled_multi_query_rag_graph` - uses multi_query_retriever
- `compiled_bm25_rag_graph` - uses bm25_retriever

#### Research Team Graph (`app/graphs/research_team.py`)
| Component | Type | Purpose | Preserve |
|-----------|------|---------|----------|
| `ResearchTeamState` | TypedDict | {messages, documents, team_members, next} | ✅ CRITICAL |
| `search_agent` | AgentExecutor | Uses video_specific_search tool | ✅ CRITICAL |
| `research_agent` | AgentExecutor | Uses retrieve_information tool | ✅ CRITICAL |
| `search_node` | Node function | Partial of agent_node | ✅ CRITICAL |
| `research_node` | Node function | Partial of agent_node_with_docs | ✅ CRITICAL |
| `research_supervisor_agent` | Runnable | Routes between VideoSearch/CommentFinder | ✅ CRITICAL |
| `research_graph` | StateGraph | Complete research team workflow | ✅ CRITICAL |
| `compiled_research_graph` | CompiledGraph | Executable | ✅ CRITICAL |

**Wrapper Functions:**
```python
def research_chain_with_docs(state):
    """Run research chain and explicitly preserve documents"""
    result = compiled_research_graph.invoke(state)
    return {
        "messages": result["messages"],
        "documents": result.get("documents", state.get("documents", []))
    }

def enter_research_chain(message: str):
    return {"messages": [HumanMessage(content=message)]}

research_chain = (
    RunnableLambda(enter_research_chain) 
    | RunnableLambda(research_chain_with_docs)
)
```

#### Analysis Team Graph (`app/graphs/analysis_team.py`)
| Component | Type | Purpose | Preserve |
|-----------|------|---------|----------|
| `SentimentState` | TypedDict | {messages, documents, team_members, next} | ✅ CRITICAL |
| `topic_agent` | AgentExecutor | Uses topic_think_tool | ✅ CRITICAL |
| `sentiment_agent` | AgentExecutor | Uses sentiment_think_tool | ✅ CRITICAL |
| `topic_node` | Node function | Partial of agent_node | ✅ CRITICAL |
| `sentiment_node` | Node function | Partial of agent_node | ✅ CRITICAL |
| `analysis_supervisor_agent` | Runnable | Routes between Topic/Sentiment | ✅ CRITICAL |
| `sentiment_graph` | StateGraph | Complete analysis workflow | ✅ CRITICAL |
| `compiled_sentiment_graph` | CompiledGraph | Executable | ✅ CRITICAL |

**Wrapper Functions:**
```python
def enter_sentiment_chain(state: dict, members: List[str]):
    return {
        "messages": [HumanMessage(content=state["message"])],
        "documents": state.get("documents", []),
        "team_members": ", ".join(members),
    }

analysis_chain = (
    RunnableLambda(functools.partial(enter_sentiment_chain, members=sentiment_graph.nodes))
    | compiled_sentiment_graph
)
```

#### Meta-Supervisor Graph (`app/graphs/supervisor.py`)
| Component | Type | Purpose | Preserve |
|-----------|------|---------|----------|
| `State` | TypedDict | {messages, documents, next} | ✅ CRITICAL |
| `super_supervisor_agent` | Runnable | Routes between Research/Analysis teams | ✅ CRITICAL |
| `get_last_message(state)` | Helper | Extract last message content | ✅ CRITICAL |
| `join_graph(response)` | Helper | Format subgraph response | ✅ CRITICAL |
| `get_messages_and_documents(state)` | Helper | Prepare analysis team input | ✅ CRITICAL |
| `super_graph` | StateGraph | Complete multi-team workflow | ✅ CRITICAL |
| `compiled_super_graph` | CompiledGraph | **MAIN ENTRY POINT** | ✅ CRITICAL |

**Node Definitions:**
```python
super_graph.add_node("Research team", get_last_message | research_chain | join_graph)
super_graph.add_node("Analysis team", get_messages_and_documents)
super_graph.add_node("SuperSupervisor", super_supervisor_agent)
```

---

### 9. **Evaluation Pipeline** (`app/evaluation/` - optional for MVP)

#### RAGAS Components
| Component | Purpose | Preserve |
|-----------|---------|----------|
| Knowledge Graph building | Transform docs into KG | ✅ Optional |
| Persona definitions | Define user types | ✅ Optional |
| TestsetGenerator | Generate synthetic queries | ✅ Optional |
| Evaluation metrics | Faithfulness, recall, precision, relevancy | ✅ Optional |

**Notes:**
- Evaluation is important but NOT required for MVP deployment
- Can be implemented as separate evaluation scripts

---

## 🗺️ Module Structure Mapping

Based on `10_Open_DeepResearch/open_deep_library` structure:

```
youtube-sentiment-chatbot/backend/app/
├── __init__.py
├── main.py                          # FastAPI app entry point
│
├── api/                             # API routes
│   ├── __init__.py
│   ├── routes.py                    # /analyze endpoint
│   └── schemas.py                   # Pydantic models for requests/responses
│
├── core/                            # Core configuration
│   ├── __init__.py
│   ├── config.py                    # Environment variables, settings
│   └── dependencies.py              # FastAPI dependencies
│
├── services/                        # External service integrations
│   ├── __init__.py
│   ├── youtube.py                   # get_youtube_comments, get_video_details, get_video_transcript
│   └── documents.py                 # create_unified_video_document, build_document_structures
│
├── retrieval/                       # Retrieval components
│   ├── __init__.py
│   ├── embeddings.py                # OpenAI embeddings setup
│   ├── vector_store.py              # Qdrant setup and management
│   ├── chunking.py                  # Text splitting logic
│   ├── retrievers.py                # Retriever configurations (qdrant, bm25, etc.)
│   └── advanced.py                  # Advanced retrievers (cohere, multi-query)
│
├── llms/                            # LLM configurations
│   ├── __init__.py
│   └── factory.py                   # LLM creation functions
│
├── prompts/                         # All prompt templates
│   ├── __init__.py
│   ├── rag.py                       # HUMAN_TEMPLATE, chat_prompt
│   ├── research.py                  # SUMMARIZATION_TEMPLATE
│   ├── agents.py                    # Agent system prompts
│   └── supervisors.py               # Supervisor prompts
│
├── tools/                           # LangChain tools
│   ├── __init__.py
│   ├── search.py                    # video_specific_search
│   ├── retrieval.py                 # retrieve_information
│   └── analysis.py                  # sentiment_think_tool, topic_think_tool
│
├── agents/                          # Agent creation utilities
│   ├── __init__.py
│   ├── factory.py                   # create_agent, create_team_supervisor
│   └── nodes.py                     # agent_node, agent_node_with_docs
│
├── graphs/                          # LangGraph workflows (FUNCTIONAL)
│   ├── __init__.py
│   ├── baseline_rag.py              # build_rag_graph() -> returns compiled graph
│   ├── research_team.py             # build_research_team_graph() -> returns compiled + chain
│   ├── analysis_team.py             # build_analysis_team_graph() -> returns compiled + chain
│   └── supervisor.py                # build_supervisor_graph() -> MAIN PIPELINE
│
├── models/                          # TypedDict state schemas
│   ├── __init__.py
│   └── state.py                     # All TypedDict definitions
│
└── evaluation/                      # Optional evaluation scripts
    ├── __init__.py
    ├── ragas_setup.py
    └── run_evaluation.py
```

---

## 🔄 Functional Paradigm Guidelines

Following `10_Open_DeepResearch/open_deep_library/deep_researcher.py`:

### ✅ DO:
1. **Factory functions** that return callables/graphs
   ```python
   def build_rag_graph(retriever, llm, prompt):
       # ... build graph
       return graph.compile()
   ```

2. **Pure functions** with explicit dependencies
   ```python
   def create_unified_video_document(video_id: str, max_comments: int = 50):
       # Takes inputs, returns outputs, no side effects
       return unified_document, raw_blobs
   ```

3. **Closures** for dependency injection
   ```python
   def build_video_search_tool(title, channel, transcript, summarization_chain):
       @tool
       def video_specific_search(query: str) -> str:
           # Has access to outer scope via closure
           ...
       return video_specific_search
   ```

4. **SimpleNamespace** for returning multiple related items
   ```python
   from types import SimpleNamespace
   
   def build_research_pipeline(artifacts):
       graph = StateGraph(...)
       compiled = graph.compile()
       chain = RunnableLambda(...) | compiled
       
       return SimpleNamespace(
           graph=graph,
           compiled=compiled,
           chain=chain,
           invoke=lambda msg: chain.invoke({"message": msg})
       )
   ```

### ❌ DON'T:
1. No classes (except TypedDict for state schemas)
2. No global mutable state
3. No singleton patterns
4. No method chaining on self

---

## 🎯 Critical Preservation Requirements

### 1. **Document Structure Integrity**
- `unified_document` must contain: video info + transcript + all comments
- `comment_docs` must be individual Document objects with metadata
- Metadata schema must match notebook exactly (used for filtering)

### 2. **Agent Prompts & Behavior**
- All system prompts must be preserved verbatim
- Tool descriptions must be preserved (they guide agent behavior)
- Supervisor routing logic must be identical

### 3. **Document Flow Through Pipeline**
- Documents must be passed through all graph states
- CommentFinder must use `agent_node_with_docs` to extract documents
- Analysis team must receive documents from research team

### 4. **Tool Access to Context**
- `video_specific_search` needs: title, channel, transcript, summarization_chain
- `retrieve_information` needs: compiled_rag_graph
- Both tools need access to video context (solve via closures, not globals)

### 5. **Graph State Schemas**
- All TypedDict definitions must be preserved
- `messages` field uses `Annotated[List[BaseMessage], operator.add]`
- `documents` field is `List[Document]`
- `next` field is `str` (for routing)

---

## 📝 Next Steps (Step 2)

1. **Create module skeletons** with function signatures
2. **Define interfaces** between modules
3. **Map notebook code** to specific module files
4. **Identify shared dependencies** (what gets passed where)
5. **Design the main orchestration function** in `supervisor.py`
6. **Plan async/streaming integration** for FastAPI

---

## ⚠️ Known Challenges to Solve

### 1. Global State in Notebook
**Problem:** `_retrieved_documents`, `title`, `channel`, `transcript`, `formatted_comments` are globals

**Solution:** Use closures or pass via dependency injection
```python
def build_tools(unified_document, raw_blobs, rag_graph):
    title = unified_document.metadata.get("title", "")
    channel = unified_document.metadata.get("channel", "")
    # ... build tools with access to this context
    return [video_search_tool, retrieval_tool]
```

### 2. Graph Wrapper Functions
**Problem:** `research_chain_with_docs`, `enter_research_chain` wrap graphs

**Solution:** Return these as part of SimpleNamespace from graph builders
```python
def build_research_team_graph(...):
    compiled = graph.compile()
    
    def enter(message: str):
        return {"messages": [HumanMessage(content=message)]}
    
    def run_with_docs(state):
        result = compiled.invoke(state)
        return {...}
    
    chain = RunnableLambda(enter) | RunnableLambda(run_with_docs)
    
    return SimpleNamespace(compiled=compiled, chain=chain, invoke=chain.invoke)
```

### 3. Streaming for FastAPI
**Problem:** Notebook uses synchronous execution

**Solution:** LangGraph supports `.stream()` - wrap in async generator
```python
async def stream_analysis(video_id: str, query: str):
    # Build pipeline
    pipeline = build_supervisor_graph(...)
    
    # Stream results
    async for chunk in pipeline.stream({"messages": [HumanMessage(content=query)]}):
        yield chunk
```

---

## 🎬 Summary

**Total Functions to Preserve:** ~30+ core functions  
**Graphs to Build:** 4 (baseline RAG, research team, analysis team, supervisor)  
**Tools to Create:** 4 (video_search, retrieve_info, sentiment_think, topic_think)  
**Agents to Configure:** 5 (search, comment, topic, sentiment, + 3 supervisors)

**Critical Path:**
1. Services (YouTube + Documents) - Foundation
2. Retrieval (Embeddings + Vector Store) - Data layer
3. LLMs + Prompts - Configuration
4. Tools - Agent capabilities
5. Agents - Reasoning components
6. Graphs - Orchestration (baseline → teams → supervisor)
7. API - FastAPI wrapper with streaming

**No steps can be skipped. Every function has a purpose.**
