# Conversation Memory Implementation

## Overview

This application now features **conversational memory** using LangGraph's checkpointing system. Users can have multi-turn conversations with the AI about a video without re-running the analysis.

## Key Features

### 🧠 Persistent Memory
- **Thread-based conversations**: Each video analysis creates a unique session (thread_id)
- **Message history**: Full conversation context maintained across questions
- **Session caching**: Video data and retrieval system cached for instant follow-ups

### 💬 Conversational Flow
1. **Initial Analysis**: User provides YouTube URL and initial question
2. **Session Created**: System generates unique session_id and caches all data
3. **Follow-up Questions**: User can ask unlimited questions about the same video
4. **Context Awareness**: AI remembers previous questions and answers

## Architecture

### Backend (Python)

#### LangGraph Checkpointer
```python
from langgraph.checkpoint.memory import MemorySaver

# Main graph compiled with memory checkpointer
checkpointer = MemorySaver()
main_graph = super_graph.compile(checkpointer=checkpointer)

# Execute with thread_id for persistence
config = {"configurable": {"thread_id": session_id}}
result = await main_graph.ainvoke(state, config)
```

#### Session Management
- **SessionManager** (`app/core/session_manager.py`): Manages conversation threads
- **VideoSession**: Stores cached data (graph, documents, retriever, raw blobs)
- **TTL**: Sessions auto-expire after 24 hours (configurable)

#### API Endpoints

**POST /api/analyze**
- Creates new session
- Fetches and caches video data
- Builds multi-agent system with memory
- Returns streaming results + session_id

**POST /api/query**
- Requires session_id from previous analysis
- Reuses cached graph and data
- Maintains conversation history
- Much faster than initial analysis

### Frontend (Next.js)

#### State Management
```typescript
const {
  sessionId,        // Current conversation thread ID
  videoInfo,        // Cached video metadata
  events,           // All conversation events
  analyzeVideo,     // Start new analysis
  askFollowUp,      // Ask follow-up question
  startNewConversation  // Reset to analyze new video
} = useStreamingAnalysis();
```

#### UI Components
1. **Session Info Badge**: Shows active conversation details
2. **Initial Analysis Input**: URL + question fields
3. **Follow-up Input**: Simple text input for additional questions
4. **Conversation History**: All Q&A pairs displayed in order

## Usage Example

### User Flow
```
1. User enters: "https://youtube.com/watch?v=abc123"
   Question: "What is the overall sentiment?"
   
   → Backend creates session: "a1b2c3d4-e5f6-7890..."
   → AI analyzes and responds
   
2. User asks follow-up: "What are the main criticisms?"
   → Same session_id used
   → AI has context from previous Q&A
   → Response considers conversation history
   
3. User asks another: "Are there any positive comments?"
   → Full conversation context maintained
   → Fast response (no re-analysis needed)
```

## Benefits

### For Users
✅ **Natural conversations** - Ask clarifying questions  
✅ **Fast follow-ups** - No need to re-analyze video  
✅ **Context preservation** - AI remembers what was discussed  
✅ **Flexible exploration** - Dive deeper into specific topics

### For System
✅ **Efficient resource usage** - Cached retrieval system  
✅ **Reduced API calls** - Video data fetched once  
✅ **Scalable** - Thread-based isolation  
✅ **Production-ready** - Session TTL and cleanup

## Configuration

### Session TTL
```python
# app/core/session_manager.py
session_manager = SessionManager(session_ttl_hours=24)
```

### Memory Checkpointer
```python
# app/graphs/main_graph.py
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # In-memory (development)
# For production, use:
# from langgraph.checkpoint.sqlite import SqliteSaver
# checkpointer = SqliteSaver("checkpoints.db")
```

## Production Considerations

### Scaling Memory Storage
- **Development**: `MemorySaver` (in-memory, lost on restart)
- **Production**: Use persistent checkpointers:
  - `SqliteSaver`: Single-server deployments
  - `PostgresSaver`: Multi-server deployments
  - Redis-based: High-performance distributed systems

### Session Cleanup
```python
# Add background task for cleanup
from fastapi_utils.tasks import repeat_every

@app.on_event("startup")
@repeat_every(seconds=3600)  # Every hour
async def cleanup_sessions():
    session_manager.cleanup_expired_sessions()
```

### Security
- Add authentication to prevent session hijacking
- Implement rate limiting per session
- Consider encrypting session data
- Add session ownership validation

## Technical Details

### State Management
```python
class SuperState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]  # Accumulated
    documents: List[Document]
    next: str
```

The `operator.add` annotation ensures messages are accumulated (not replaced) across graph executions, maintaining full conversation history.

### Thread Isolation
Each `thread_id` (session_id) maintains separate:
- Message history
- Intermediate state
- Checkpoints

This enables multiple users to have parallel conversations without interference.

## API Response Format

### Session Created Event
```json
{
  "type": "session_created",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "video_id": "dQw4w9WgXcQ",
  "title": "Example Video",
  "channel": "Example Channel"
}
```

### Final Response
```json
{
  "type": "final",
  "content": "Analysis result in markdown...",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "documents": [...]
}
```

## Resources

- [LangGraph Memory Docs](https://docs.langchain.com/oss/python/concepts/memory)
- [LangGraph Checkpointing](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Short-term Memory Guide](https://docs.langchain.com/oss/python/langchain/short-term-memory)
