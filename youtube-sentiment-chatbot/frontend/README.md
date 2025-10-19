# YouTube Sentiment Analyzer - Frontend

Next.js + React + TypeScript frontend for the YouTube Sentiment Analyzer.

## Features

- **Real-time Streaming**: Watch multi-agent analysis in real-time via Server-Sent Events
- **Responsive UI**: Beautiful, responsive design with Tailwind CSS
- **Type-Safe**: Full TypeScript support
- **Agent Visibility**: See each agent's messages as they work
- **Progress Tracking**: Visual feedback during analysis
- **Document Display**: View retrieved comments and context

## Tech Stack

- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Markdown** - Markdown rendering for agent messages

## Project Structure

```
src/
├── app/
│   ├── globals.css       # Global styles with Tailwind
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Main page
├── components/
│   ├── URLInput.tsx      # YouTube URL input form
│   └── StreamingDisplay.tsx # Real-time analysis display
├── hooks/
│   └── useStreamingAnalysis.ts # Custom hook for streaming
└── lib/
    ├── api.ts            # API client for backend communication
    └── types.ts          # TypeScript type definitions
```

## Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local if needed (default: http://localhost:8000)
```

## Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

## Build for Production

```bash
# Build
npm run build

# Start production server
npm start
```

## Usage

1. **Enter YouTube URL**: Paste any YouTube video URL
2. **Adjust Parameters**:
   - Max Comments: 10-200 (default: 50)
   - Question: Customize what to analyze
3. **Click "Analyze Video"**: Watch the multi-agent system work in real-time
4. **View Results**: See progress messages, agent messages, and final analysis

## Component Details

### URLInput Component

- YouTube URL input
- Max comments slider (10-200)
- Customizable question textarea
- Loading state with spinner
- Form validation

### StreamingDisplay Component

- Real-time event streaming
- Different card styles for event types:
  - **Progress** (blue): System progress updates
  - **Agent Messages** (green): Messages from agents (VideoSearch, CommentFinder, Sentiment, Topic)
  - **Final** (purple): Final analysis result
  - **Error** (red): Error messages
- Auto-scroll to latest event
- Markdown rendering for agent messages
- Document preview for final responses

### useStreamingAnalysis Hook

Custom React hook that:
- Manages streaming state
- Handles Server-Sent Events
- Accumulates events
- Provides error handling
- Exposes `analyzeVideo` and `clearEvents` functions

### API Client

TypeScript client for backend communication:
- `analyzeVideo()`: POST to /api/analyze with streaming
- `healthCheck()`: GET /api/health
- Automatic JSON parsing of events
- Error handling

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Styling

Uses Tailwind CSS with:
- Responsive design (mobile-first)
- Dark mode support
- Custom color scheme
- Smooth transitions and animations
- Loading spinners
- Auto-scrolling

## Type Safety

Full TypeScript coverage:
- StreamEvent types (Progress, AgentMessage, Final, Error)
- API request/response models
- Component props
- Hook return values

## Browser Support

Requires modern browsers with:
- Fetch API
- ReadableStream
- Server-Sent Events (EventSource simulation via fetch)

## Troubleshooting

**Connection Refused**: Make sure backend is running on http://localhost:8000

**CORS Errors**: Backend must have CORS enabled for http://localhost:3000

**No Events Streaming**: Check browser console for fetch errors

**Build Errors**: Run `npm install` to ensure all dependencies are installed

## Next Steps

- [ ] Add video preview
- [ ] Add sentiment visualization (charts)
- [ ] Add comment filtering/search
- [ ] Add export results feature
- [ ] Add analysis history
- [ ] Add authentication
