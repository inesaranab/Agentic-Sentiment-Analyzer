/**
 * Custom hook for streaming video analysis with conversation memory
 */

import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { StreamEventType } from "@/lib/types";

export function useStreamingAnalysis() {
  const [events, setEvents] = useState<StreamEventType[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [videoInfo, setVideoInfo] = useState<{
    videoId: string;
    title: string;
    channel: string;
  } | null>(null);

  const analyzeVideo = useCallback(
    async (url: string, maxComments: number, question: string) => {
      setIsStreaming(true);
      setError(null);

      await apiClient.analyzeVideo(
        { url, max_comments: maxComments, question },
        (event: StreamEventType) => {
          setEvents((prev) => [...prev, event]);
          
          // Capture session_id when created
          if (event.type === "session_created") {
            setSessionId(event.session_id);
            setVideoInfo({
              videoId: event.video_id,
              title: event.title,
              channel: event.channel,
            });
          }
        },
        (err: Error) => {
          setError(err);
          setIsStreaming(false);
        }
      );

      setIsStreaming(false);
    },
    []
  );

  const askFollowUp = useCallback(
    async (question: string) => {
      if (!sessionId) {
        setError(new Error("No active session. Please analyze a video first."));
        return;
      }

      setIsStreaming(true);
      setError(null);

      await apiClient.queryVideo(
        { session_id: sessionId, question },
        (event: StreamEventType) => {
          setEvents((prev) => [...prev, event]);
        },
        (err: Error) => {
          setError(err);
          setIsStreaming(false);
        }
      );

      setIsStreaming(false);
    },
    [sessionId]
  );

  const clearEvents = useCallback(() => {
    setEvents([]);
    setError(null);
  }, []);

  const startNewConversation = useCallback(() => {
    setEvents([]);
    setError(null);
    setSessionId(null);
    setVideoInfo(null);
  }, []);

  return {
    events,
    isStreaming,
    error,
    sessionId,
    videoInfo,
    analyzeVideo,
    askFollowUp,
    clearEvents,
    startNewConversation,
  };
}
