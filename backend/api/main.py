"""
main.py — FastAPI application with SSE streaming.

Endpoints:
    POST /tour/generate     — generate a tour (SSE stream)
    GET  /tour/{cache_key}  — get cached tour manifest
    GET  /tour/{cache_key}/files/{filename} — serve tour files (MP3, GeoJSON)

Cache check:
    Before running the pipeline, check if the tour package already
    exists in backend/storage/. If yes, stream a CACHED event and
    return immediately — no LLM or TTS calls needed.
"""

import json
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from backend.agents.state import TourState
from backend.agents.graph import tour_graph
from backend.api.streaming import progress, success, error, cached

# ------------------------------------------------------------------ #
# App setup
# ------------------------------------------------------------------ #
app = FastAPI(
    title="Iraqi Heritage Audio Tour API",
    description="Multi-agent pipeline for generating heritage audio tours.",
    version="1.0.0",
)

# Allow Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_DIR = Path("backend/storage")

# ------------------------------------------------------------------ #
# Request schema
# ------------------------------------------------------------------ #
class TourRequest(BaseModel):
    site_id:       str   # "babylon" | "ur" | "erbil_citadel"
    duration_mins: int   # 30 | 60 | 90

    def cache_key(self) -> str:
        return f"{self.site_id}_{self.duration_mins}"


# ------------------------------------------------------------------ #
# Cache check
# ------------------------------------------------------------------ #
def is_cached(cache_key: str) -> bool:
    """Check if a tour package already exists in storage."""
    manifest = STORAGE_DIR / cache_key / "manifest.json"
    return manifest.exists()


def get_manifest(cache_key: str) -> dict:
    """Load and return the tour manifest JSON."""
    manifest_path = STORAGE_DIR / cache_key / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ #
# SSE generator
# ------------------------------------------------------------------ #
async def generate_tour_stream(request: TourRequest) -> AsyncGenerator[str, None]:
    """
    Async generator that runs the pipeline and yields SSE events.
    Uses LangGraph's stream() to get per-node progress updates.
    """
    cache_key = request.cache_key()

    # ── Cache check ───────────────────────────────────────────── #
    if is_cached(cache_key):
        manifest = get_manifest(cache_key)
        yield cached(
            f"Tour already generated — serving from cache.",
            data={"cache_key": cache_key, "manifest": manifest}
        )
        return

    # ── Node message map ──────────────────────────────────────── #
    node_messages = {
        "stop_selector": "Choosing your tour stops...",
        "retriever":     "Gathering historical knowledge...",
        "narrator":      "AI is writing your tour narration...",
        "verifier":      "Fact-checking all claims...",
        "router":        "Planning your walking route...",
        "stitcher":      "Assembling your tour script...",
        "tts":           "Generating audio for each stop...",
    }

    # ── Run pipeline with streaming ───────────────────────────── #
    try:
        initial_state = TourState(
            site_id=request.site_id,
            duration_mins=request.duration_mins,
        )

        # stream() yields {node_name: state_delta} dicts as each node completes
        for update in tour_graph.stream(initial_state, stream_mode="updates"):
            for node_name in update:
                message = node_messages.get(node_name, f"{node_name} complete.")
                yield progress(f"✓ {message}")

        # Pipeline complete — load and return the manifest
        manifest = get_manifest(cache_key)
        yield success(
            "Your audio tour is ready!",
            data={"cache_key": cache_key, "manifest": manifest}
        )

    except Exception as e:
        yield error(f"Pipeline failed: {str(e)}")


# ------------------------------------------------------------------ #
# Endpoints
# ------------------------------------------------------------------ #
@app.post("/tour/generate")
async def generate_tour(request: TourRequest):
    """
    Generate an audio tour for a site and duration.
    Returns a Server-Sent Events stream with pipeline progress.
    """
    # Validate inputs
    if request.site_id not in ["babylon", "ur", "erbil_citadel"]:
        raise HTTPException(status_code=400, detail=f"Unknown site_id: {request.site_id}")
    if request.duration_mins not in [30, 60, 90]:
        raise HTTPException(status_code=400, detail=f"duration_mins must be 30, 60, or 90.")

    return EventSourceResponse(generate_tour_stream(request))


@app.get("/tour/{cache_key}")
async def get_tour(cache_key: str):
    """
    Return the manifest for a cached tour package.
    """
    if not is_cached(cache_key):
        raise HTTPException(status_code=404, detail=f"Tour '{cache_key}' not found.")
    return get_manifest(cache_key)


@app.get("/tour/{cache_key}/files/{filename}")
async def get_tour_file(cache_key: str, filename: str):
    """
    Serve a tour file (MP3 or GeoJSON) from storage.
    """
    file_path = STORAGE_DIR / cache_key / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
    return FileResponse(file_path)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "Iraqi Heritage Audio Tour API"}
