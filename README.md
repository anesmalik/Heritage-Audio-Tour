# Echoes of Mesopotamia — AI Heritage Audio Tour

An AI-powered audio tour generator for Iraqi archaeological sites. Select a site and duration, and a multi-agent pipeline writes, fact-checks, and narrates a personalised walking tour — then streams it live to your browser.

![Tour page showing Babylon with map and audio player](docs/screenshot.png)

---

## Sites

| Site | Period |
|---|---|
| **Babylon** | Neo-Babylonian Empire · 626–539 BC |
| **Ur** | Third Dynasty of Ur · 2112–2004 BC |
| **Erbil Citadel** | Continuously inhabited · 6,000+ years |

## Architecture

```
Frontend (Next.js)  ──POST──►  Backend (FastAPI)
                                    │
                              LangGraph pipeline
                                    │
                    ┌───────────────▼───────────────┐
                    │  stop_selector                 │
                    │  retriever  (Chroma RAG)       │
                    │  narrator   (GPT-4o-mini)      │
                    │  verifier   (fact-check)       │◄─ retry loop
                    │  router     (walking order)    │
                    │  stitcher   (final script)     │
                    │  tts        (OpenAI TTS)       │
                    └───────────────────────────────┘
                                    │
                         SSE stream → browser
```

Progress events are streamed to the frontend in real time via Server-Sent Events. Completed tours are cached — subsequent requests for the same site/duration are served instantly.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/api-keys)

---

## Setup

### 1. Clone

```bash
git clone https://github.com/your-username/heritage-audio-tour.git
cd heritage-audio-tour
```

### 2. Backend

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your OpenAI API key
```

Build the vector corpus (scrapes Wikipedia, chunks, and embeds):

```bash
python -m backend.corpus.ingest
```

Start the API server:

```bash
uvicorn backend.api.main:app --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Usage

1. Pick a site — Babylon, Ur, or Erbil Citadel
2. Choose a duration — 30, 60, or 90 minutes
3. Click **Generate My Audio Tour**
4. Watch the pipeline run live, then walk your tour with audio and an interactive map
5. Download individual audio stops or save the map as an image

---

## Project Structure

```
heritage-audio-tour/
├── backend/
│   ├── agents/          # LangGraph nodes (stop_selector, narrator, verifier …)
│   ├── api/             # FastAPI app + SSE streaming
│   ├── corpus/          # Wikipedia scraper, chunker, Chroma vector store
│   ├── sites/           # YAML definitions for each heritage site
│   ├── storage/         # Generated tours (gitignored)
│   └── tts/             # OpenAI TTS wrapper
├── frontend/
│   └── app/
│       ├── page.tsx             # Home — site & duration selection
│       ├── generating/page.tsx  # Live pipeline progress
│       ├── tour/[cache_key]/    # Tour playback page
│       └── components/TourMap.tsx
├── requirements.txt
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, Tailwind CSS, Leaflet |
| Backend | FastAPI, uvicorn, sse-starlette |
| Agents | LangGraph, LangChain, GPT-4o-mini |
| Vector store | ChromaDB |
| TTS | OpenAI TTS API |

---

## Disclaimer

Audio narration is AI-generated. All factual content is sourced from Wikipedia. Not a substitute for professional guides.
