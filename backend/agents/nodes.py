"""
nodes.py — Stub implementations of all 6 LangGraph nodes.

Responsibility: Define the function signature and logging for each node.
In Step 4, each stub will be replaced with real agent logic.
Every node receives a TourState and returns an updated TourState.

Node order:
    stop_selector → retriever → narrator → verifier → router → stitcher
                                              ↑           |
                                              └───────────┘
                                         (conditional retry edge)
"""

from backend.agents.state import TourState, Stop
from backend.agents.stop_selector import stop_selector
from backend.agents.retriever import retriever
from backend.agents.narrator import narrator
from backend.agents.verifier import verifier
from backend.agents.router import router
from backend.agents.stitcher import stitcher
from backend.tts.tts import tts

# ------------------------------------------------------------------ #
# Verifier
# Checks every claim in the narration has a valid citation
# ------------------------------------------------------------------ #

def should_retry(state: TourState) -> str:
    """
    Conditional edge function — called after verifier.
    Returns the name of the next node to route to.

    Routes to:
        "narrator"  — if verification failed and retries remain
        "router"    — if verification passed or max retries reached
    """
    if not state.verification_passed and state.retry_count < state.MAX_RETRIES:
        state.retry_count += 1
        print(f"[verifier] Verification failed — retry {state.retry_count}/{state.MAX_RETRIES}")
        return "narrator"

    if state.retry_count >= state.MAX_RETRIES:
        print(f"[verifier] Max retries reached — proceeding anyway.")

    return "router"