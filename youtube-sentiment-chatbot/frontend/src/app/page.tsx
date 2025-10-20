"use client";

import { useState, useEffect } from "react";
import { useStreamingAnalysis } from "@/hooks/useStreamingAnalysis";
import { Loader2, Sparkles, CheckCircle2, XCircle, MessageSquare, Send, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function Home() {
  const { events, isStreaming, error, sessionId, videoInfo, analyzeVideo, askFollowUp, clearEvents, startNewConversation } = useStreamingAnalysis();
  const [url, setUrl] = useState("");
  const [question, setQuestion] = useState("What is the overall sentiment of the comments on this video?");
  const [followUpQuestion, setFollowUpQuestion] = useState("");

  const handleAnalyze = async () => {
    if (!url.trim()) return;
    clearEvents();
    await analyzeVideo(url, 50, question || "What is the overall sentiment of the comments on this video?");
  };

  const handleFollowUp = async () => {
    if (!followUpQuestion.trim() || !sessionId) return;
    await askFollowUp(followUpQuestion);
    setFollowUpQuestion(""); // Clear input after asking
  };

  const handleNewAnalysis = () => {
    setUrl("");
    setQuestion("What is the overall sentiment of the comments on this video?");
    setFollowUpQuestion("");
    startNewConversation();
  };
  
  // Derived state
  const isComplete = events.some(e => e.type === "final") && !isStreaming;

  // Get all final results (could be multiple in conversation)
  const finalEvents = events.filter(e => e.type === "final");
  
  // Get all agent messages (these contain the actual analysis from each agent)
  const agentMessages = events.filter(e => e.type === "agent_message");
  
  // Group agent messages by "conversation turn" - split by session_created events
  const conversationTurns: typeof agentMessages[] = [];
  let currentTurn: typeof agentMessages = [];
  
  events.forEach(event => {
    if (event.type === "agent_message") {
      currentTurn.push(event);
    } else if (event.type === "final" && currentTurn.length > 0) {
      conversationTurns.push([...currentTurn]);
      currentTurn = [];
    }
  });
  
  // Add any remaining messages
  if (currentTurn.length > 0) {
    conversationTurns.push(currentTurn);
  }
  
  const hasStarted = events.length > 0;
  const hasSession = sessionId !== null;

  // Debug logging
  useEffect(() => {
    console.log("Events:", events.length);
    console.log("Final events:", finalEvents.length);
    console.log("Agent messages:", agentMessages.length);
    console.log("Conversation turns:", conversationTurns.length);
    console.log("Event types:", events.map(e => e.type));
  }, [events, finalEvents, agentMessages, conversationTurns]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-8 h-8 text-red-500" />
            <h1 className="text-4xl font-bold text-white">
              YouTube <span className="text-red-500">Sentiment</span> AI
            </h1>
          </div>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Analyze YouTube videos with multi-agent AI. Get deep insights and ask follow-up questions in a conversation.
          </p>
        </div>

        {/* Session Info Badge */}
        {hasSession && videoInfo && (
          <div className="bg-indigo-50 dark:bg-indigo-950/30 rounded-xl border border-indigo-200 dark:border-indigo-800 p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-indigo-900 dark:text-indigo-100 text-sm">
                  Active Conversation
                </h3>
                <p className="text-xs text-indigo-700 dark:text-indigo-300 mt-1">
                  {videoInfo.title} • {videoInfo.channel}
                </p>
              </div>
              <button
                onClick={handleNewAnalysis}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors text-sm flex items-center gap-1"
              >
                <RefreshCw className="w-4 h-4" />
                New Video
              </button>
            </div>
          </div>
        )}

        {/* Input Card - Initial Analysis */}
        {!hasStarted && (
          <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-8 mb-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  YouTube URL
                </label>
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleAnalyze()}
                  disabled={isStreaming}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  <MessageSquare className="w-4 h-4 inline mr-1" />
                  Your Question
                </label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="What would you like to know about this video?"
                  rows={3}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
                  disabled={isStreaming}
                />
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  Example questions: "What are the main topics discussed?", "How do viewers feel about the content?", "What are common criticisms?"
                </p>
              </div>
              
              <button
                onClick={handleAnalyze}
                disabled={isStreaming || !url.trim()}
                className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 disabled:from-slate-400 disabled:to-slate-500 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl disabled:cursor-not-allowed"
              >
                {isStreaming ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Analyze Video
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Progress Indicator */}
        {isStreaming && (
          <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-6 mb-6">
            <div className="flex items-center gap-4">
              <Loader2 className="w-6 h-6 text-indigo-600 dark:text-indigo-400 animate-spin flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
                  {hasSession ? "Processing your question..." : "Analysis in Progress"}
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {events.length > 0 ? events[events.length - 1].content : "Initializing..."}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Completion Badge */}
        {isComplete && !error && !isStreaming && (
          <div className="bg-green-50 dark:bg-green-950/30 rounded-2xl shadow-xl border border-green-200 dark:border-green-800 p-6 mb-6">
            <div className="flex items-center gap-4">
              <CheckCircle2 className="w-8 h-8 text-green-600 dark:text-green-400 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 dark:text-green-100 text-lg">
                  {hasSession ? "Answer Ready!" : "Analysis Complete!"}
                </h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  {hasSession ? "You can ask another question below." : "Your video has been analyzed. Ask follow-up questions!"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 dark:bg-red-950/30 rounded-2xl shadow-xl border border-red-200 dark:border-red-800 p-6 mb-6">
            <div className="flex items-center gap-4">
              <XCircle className="w-8 h-8 text-red-600 dark:text-red-400 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-900 dark:text-red-100 text-lg">
                  Error
                </h3>
                <p className="text-sm text-red-700 dark:text-red-300">
                  {error.message}
                </p>
              </div>
              <button
                onClick={handleNewAnalysis}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Conversation Results - Show ALL agent responses */}
        {conversationTurns.length > 0 && (
          <div className="space-y-6 mb-6">
            {conversationTurns.map((turn, turnIdx) => (
              <div key={turnIdx} className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    {turnIdx === 0 ? "Analysis Results" : `Follow-up Answer ${turnIdx}`}
                  </h2>
                  {turnIdx === conversationTurns.length - 1 && (
                    <span className="text-xs text-green-600 dark:text-green-400 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" />
                      Latest
                    </span>
                  )}
                </div>
                
                {/* Display all agent messages in this turn */}
                <div className="space-y-4">
                  {turn.map((event, msgIdx) => {
                    // Extract agent name from the event
                    const agentName = event.metadata?.agent_name || event.metadata?.langgraph_node || 'Agent';
                    const isImportant = agentName.toLowerCase().includes('supervisor');
                    
                    return (
                      <div key={msgIdx} className={`p-5 rounded-xl border-2 transition-all ${
                        isImportant 
                          ? 'bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-950/30 dark:to-blue-950/30 border-indigo-300 dark:border-indigo-700' 
                          : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700'
                      }`}>
                        {/* Agent Badge */}
                        <div className="flex items-center gap-2 mb-3">
                          <div className={`w-2.5 h-2.5 rounded-full ${
                            isImportant 
                              ? 'bg-indigo-600 dark:bg-indigo-400 animate-pulse' 
                              : 'bg-slate-400 dark:bg-slate-500'
                          }`} />
                          <span className={`text-sm font-bold tracking-wide ${
                            isImportant
                              ? 'text-indigo-700 dark:text-indigo-300'
                              : 'text-slate-600 dark:text-slate-400'
                          }`}>
                            {agentName.charAt(0).toUpperCase() + agentName.slice(1).replace(/_/g, ' ')}
                          </span>
                          {isImportant && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-200 dark:bg-indigo-800 text-indigo-800 dark:text-indigo-200 font-semibold">
                              LEAD
                            </span>
                          )}
                        </div>
                        
                        {/* Message Content */}
                        <div className="prose prose-slate dark:prose-invert max-w-none
                          prose-headings:text-slate-900 dark:prose-headings:text-slate-100
                          prose-p:text-slate-700 dark:prose-p:text-slate-300
                          prose-strong:text-slate-900 dark:prose-strong:text-slate-100
                          prose-a:text-indigo-600 dark:prose-a:text-indigo-400
                          prose-code:text-indigo-600 dark:prose-code:text-indigo-400
                          prose-pre:bg-slate-100 dark:prose-pre:bg-slate-800
                          prose-ul:text-slate-700 dark:prose-ul:text-slate-300
                          prose-ol:text-slate-700 dark:prose-ol:text-slate-300
                          prose-li:text-slate-700 dark:prose-li:text-slate-300">
                          {event.content && (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {event.content}
                            </ReactMarkdown>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Follow-up Question Input */}
        {hasSession && isComplete && !isStreaming && (
          <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-6">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              Ask a Follow-up Question
            </h3>
            <div className="flex gap-3">
              <input
                type="text"
                value={followUpQuestion}
                onChange={(e) => setFollowUpQuestion(e.target.value)}
                placeholder="Ask anything about this video..."
                className="flex-1 px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                onKeyDown={(e) => e.key === "Enter" && handleFollowUp()}
                disabled={isStreaming}
              />
              <button
                onClick={handleFollowUp}
                disabled={isStreaming || !followUpQuestion.trim()}
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 disabled:from-slate-400 disabled:to-slate-500 text-white font-semibold rounded-lg transition-all duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
                Ask
              </button>
            </div>
            <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
              Examples: "What controversial topics are mentioned?", "Are there any recurring complaints?", "What do people praise most?"
            </p>
          </div>
        )}

        {/* Process Steps (collapsed view) */}
        {hasStarted && events.length > 1 && (
          <details className="mt-6 bg-white/60 dark:bg-slate-900/60 backdrop-blur-sm rounded-xl border border-slate-200 dark:border-slate-800 p-4">
            <summary className="cursor-pointer text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400">
              View Analysis Steps ({events.filter(e => e.type !== "final" && e.type !== "session_created").length})
            </summary>
            <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
              {events.filter(e => e.type !== "final" && e.type !== "session_created").map((event, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-sm">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0"></div>
                  <span className="text-slate-600 dark:text-slate-400">{event.content}</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </main>
  );
}
