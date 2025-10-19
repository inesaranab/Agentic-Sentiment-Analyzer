/**
 * Streaming Display Component
 * Shows real-time progress and agent messages during analysis
 */

import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { StreamEventType } from "@/lib/types";

interface StreamingDisplayProps {
  events: StreamEventType[];
}

export default function StreamingDisplay({ events }: StreamingDisplayProps) {
  const endRef = useRef<HTMLDivElement>(null);
  
  // Check if analysis is complete
  const isComplete = events.some(event => event.type === "final" || event.type === "error");

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Analysis {isComplete ? "Complete" : "Progress"}
        </h2>
        {isComplete && (
          <span className="px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full text-sm font-semibold flex items-center gap-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            Finished
          </span>
        )}
      </div>

      <div className="space-y-4 max-h-[600px] overflow-y-auto">
        {events.map((event, index) => (
          <EventCard key={index} event={event} />
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}

function EventCard({ event }: { event: StreamEventType }) {
  const getCardStyle = (type: string) => {
    switch (type) {
      case "progress":
        return "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800";
      case "agent_message":
        return "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800";
      case "final":
        return "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800";
      case "error":
        return "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800";
      default:
        return "bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600";
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "progress":
        return (
          <svg
            className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        );
      case "agent_message":
        return (
          <svg
            className="w-5 h-5 text-green-600 dark:text-green-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
          </svg>
        );
      case "final":
        return (
          <svg
            className="w-5 h-5 text-purple-600 dark:text-purple-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "error":
        return (
          <svg
            className="w-5 h-5 text-red-600 dark:text-red-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getCardStyle(event.type)}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">{getIcon(event.type)}</div>

        <div className="flex-1 min-w-0">
          {/* Agent name for agent messages */}
          {"agent" in event && (
            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
              {event.agent}
            </p>
          )}

          {/* Event content */}
          <div className="text-sm text-gray-700 dark:text-gray-300 prose dark:prose-invert max-w-none">
            <ReactMarkdown>{event.content}</ReactMarkdown>
          </div>

          {/* Documents for final response */}
          {event.type === "final" && "documents" in event && event.documents && (
            <div className="mt-4">
              <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
                Retrieved Documents ({event.documents.length})
              </p>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {event.documents.slice(0, 5).map((doc, idx) => (
                  <div
                    key={idx}
                    className="text-xs bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600"
                  >
                    <p className="font-semibold text-gray-700 dark:text-gray-300">
                      {doc.metadata.type === "comment"
                        ? `Comment by ${doc.metadata.author}`
                        : "Video Context"}
                    </p>
                    <p className="text-gray-600 dark:text-gray-400 truncate">
                      {doc.content.substring(0, 100)}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
