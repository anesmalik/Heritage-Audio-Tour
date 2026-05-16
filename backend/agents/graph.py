"""
graph.py — LangGraph graph wiring.

Responsibility: Connect all nodes and edges into a compiled graph.
This file only wires — it contains no business logic.
All logic lives in nodes.py.

Graph structure:
    START
      │
      ▼
  stop_selector
      │
      ▼
   retriever
      │
      ▼
   narrator  ◄──────────────┐
      │                      │ (retry if verification failed)
      ▼                      │
   verifier ─── should_retry ┤
                             │
                             ▼
                           router
                             │
                             ▼
                          stitcher
                             │
                             ▼
                            tts
                             │
                             ▼
                            END
"""

from langgraph.graph import StateGraph, END

from backend.agents.state import TourState
from backend.agents.nodes import (
    stop_selector,
    retriever,
    narrator,
    verifier,
    should_retry,
    router,
    stitcher,
    tts,
)


def build_graph():
    """
    Build and compile the LangGraph pipeline.

    Returns a compiled graph ready to invoke with:
        graph.invoke(TourState(site_id="babylon", duration_mins=60))
    """

    # ── Initialize graph with our state schema ─────────────────── #
    workflow = StateGraph(TourState)

    # ── Register nodes ─────────────────────────────────────────── #
    workflow.add_node("stop_selector", stop_selector)
    workflow.add_node("retriever",     retriever)
    workflow.add_node("narrator",      narrator)
    workflow.add_node("verifier",      verifier)
    workflow.add_node("router",        router)
    workflow.add_node("stitcher",      stitcher)
    workflow.add_node("tts",           tts)

    # ── Define edges (linear flow) ─────────────────────────────── #
    workflow.set_entry_point("stop_selector")

    workflow.add_edge("stop_selector", "retriever")
    workflow.add_edge("retriever",     "narrator")
    workflow.add_edge("narrator",      "verifier")

    # ── Conditional edge — verifier can retry narrator ─────────── #
    workflow.add_conditional_edges(
        "verifier",        # source node
        should_retry,      # edge function — returns "narrator" or "router"
        {
            "narrator": "narrator",   # retry path
            "router":   "router",     # success path
        }
    )

    workflow.add_edge("router",   "stitcher")
    workflow.add_edge("stitcher", "tts")
    workflow.add_edge("tts",      END)

    # ── Compile and return ─────────────────────────────────────── #
    return workflow.compile()


# ── Module-level compiled graph — imported by the API layer ────── #
tour_graph = build_graph()


# ------------------------------------------------------------------ #
# Smoke test — run directly to verify the graph compiles and runs:
#   python -m backend.agents.graph
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    print("[graph] Building graph...")
    graph = build_graph()

    print("[graph] Running smoke test with stub nodes...\n")
    result = graph.invoke(
        TourState(site_id="babylon", duration_mins=60)
    )

    print(f"\n[graph] ✓ Graph completed.")
    print(f"[graph] cache_key        : {result['cache_key']}")
    print(f"[graph] verification     : {result['verification_passed']}")
    print(f"[graph] selected_stops   : {len(result['selected_stops'])}")
    print(f"[graph] ordered_stops    : {len(result['ordered_stops'])}")
    print(f"[graph] final_script     : {result.get('final_script', None)}")
