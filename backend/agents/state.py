"""
state.py — Shared state schema for the LangGraph pipeline.

Responsibility: Define the single state object that flows through
every node in the graph. Each node reads from it and writes back
to it. Pydantic enforces types at runtime so bad data fails fast
rather than silently corrupting downstream nodes.

State lifecycle:
    1. Initialized by the API with site_id + duration
    2. Passed to stop_selector → retriever → narrator → verifier → router → stitcher
    3. Final state contains the complete tour package ready for TTS
"""

from typing import Optional
from pydantic import BaseModel, Field


class Stop(BaseModel):
    """
    A single tour stop — selected from the site YAML candidate list.
    Gets enriched as it passes through each node.
    """
    id:          str                    # e.g. "babylon_ishtar_gate"
    name:        str                    # e.g. "Ishtar Gate"
    coordinates: list[float]           # [longitude, latitude]
    keywords:    list[str]             # retrieval handles from YAML
    description: str                   # editorial note from YAML

    # Populated by retriever node
    chunks:      list[dict] = Field(default_factory=list)

    # Populated by narrator node
    narration:   Optional[str] = None

    # Populated by verifier node
    verified:    bool = False
    citations:   list[str] = Field(default_factory=list)  # chunk_ids cited


class TourState(BaseModel):
    """
    The master state object passed between all nodes in the graph.

    Fields are grouped by which node populates them so it's easy
    to trace where each piece of data comes from.
    """

    # ── Input (set by API before graph starts) ─────────────────── #
    site_id:       str                          # "babylon" | "ur" | "erbil_citadel"
    duration_mins: int                          # 30 | 60 | 90

    # ── stop_selector output ───────────────────────────────────── #
    selected_stops: list[Stop] = Field(default_factory=list)

    # ── retriever output ───────────────────────────────────────── #
    # Chunks are stored inside each Stop object (stop.chunks)
    # so retrieval stays scoped per stop

    # ── narrator output ────────────────────────────────────────── #
    # Narration stored inside each Stop object (stop.narration)

    # ── verifier output ────────────────────────────────────────── #
    verification_passed: bool = False
    retry_count:         int  = 0
    MAX_RETRIES:         int  = 3           # hard limit on verifier retries

    # ── router output ──────────────────────────────────────────── #
    ordered_stops: list[Stop] = Field(default_factory=list)

    # ── stitcher output ────────────────────────────────────────── #
    final_script:  Optional[str]  = None   # full narration script as string
    geojson_route: Optional[dict] = None   # GeoJSON FeatureCollection

    # ── pipeline metadata ──────────────────────────────────────── #
    error:         Optional[str]  = None   # set if any node fails
    cache_key:     Optional[str]  = None   # "{site_id}_{duration_mins}"


    def model_post_init(self, __context) -> None:
        """Auto-generate cache key on initialization."""
        self.cache_key = f"{self.site_id}_{self.duration_mins}"
