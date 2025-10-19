/**
 * TypeScript types for the YouTube Sentiment Analyzer frontend
 */

export interface StreamEvent {
  type: "progress" | "agent_message" | "final" | "error" | "session_created";
  content: string;
  session_id?: string;
}

export interface SessionCreatedEvent extends StreamEvent {
  type: "session_created";
  session_id: string;
  video_id: string;
  title: string;
  channel: string;
}

export interface AgentMessageEvent extends StreamEvent {
  type: "agent_message";
  agent: string;
  session_id?: string;
  metadata?: {
    agent_name?: string;
    langgraph_node?: string;
    [key: string]: any;
  };
}

export interface FinalResponseEvent extends StreamEvent {
  type: "final";
  session_id?: string;
  documents?: RetrievedDocument[];
}

export interface ErrorEvent extends StreamEvent {
  type: "error";
}

export interface ProgressEvent extends StreamEvent {
  type: "progress";
}

export interface RetrievedDocument {
  content: string;
  metadata: {
    type: string;
    video_id?: string;
    title?: string;
    author?: string;
    likes?: number;
    published?: string;
    [key: string]: any;
  };
}

export interface VideoAnalysisRequest {
  url: string;
  max_comments?: number;
  question?: string;
}

export interface QueryRequest {
  session_id: string;
  question: string;
}

export type StreamEventType =
  | ProgressEvent
  | AgentMessageEvent
  | FinalResponseEvent
  | ErrorEvent
  | SessionCreatedEvent;
