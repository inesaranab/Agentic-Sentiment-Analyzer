/**
 * URL Input Component
 * Allows users to input YouTube URL and configure analysis parameters
 */

import { useState } from "react";

interface URLInputProps {
  onAnalyze: (url: string, maxComments: number, question: string) => void;
  isAnalyzing: boolean;
}

export default function URLInput({ onAnalyze, isAnalyzing }: URLInputProps) {
  const [url, setUrl] = useState("");
  const [maxComments, setMaxComments] = useState(50);
  const [question, setQuestion] = useState(
    "What is the overall sentiment of the comments on this video?"
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      alert("Please enter a YouTube URL");
      return;
    }

    onAnalyze(url, maxComments, question);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* YouTube URL Input */}
        <div>
          <label
            htmlFor="url"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            YouTube URL
          </label>
          <input
            type="text"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            disabled={isAnalyzing}
          />
        </div>

        {/* Max Comments Slider */}
        <div>
          <label
            htmlFor="maxComments"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Max Comments: <span className="font-bold">{maxComments}</span>
          </label>
          <input
            type="range"
            id="maxComments"
            min="10"
            max="200"
            step="10"
            value={maxComments}
            onChange={(e) => setMaxComments(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            disabled={isAnalyzing}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>10</span>
            <span>200</span>
          </div>
        </div>

        {/* Question Input */}
        <div>
          <label
            htmlFor="question"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            disabled={isAnalyzing}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isAnalyzing}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
        >
          {isAnalyzing ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
              Analyzing...
            </>
          ) : (
            "Analyze Video"
          )}
        </button>
      </form>
    </div>
  );
}
