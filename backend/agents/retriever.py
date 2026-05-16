"""
retriever.py — Real implementation of the retriever node.

Responsibility: For each selected stop, query ChromaDB using the
stop's keywords and populate stop.chunks with the most relevant
corpus chunks.

This node has NO LLM call — it's pure vector search.
The quality of retrieval directly determines narration quality.
"""

from backend.agents.state import TourState
from backend.corpus.chroma_store import query_chunks


# ------------------------------------------------------------------ #
# How many chunks to retrieve per stop keyword query
# More chunks = more context for narrator, but higher token cost
# ------------------------------------------------------------------ #
CHUNKS_PER_KEYWORD = 3
MAX_CHUNKS_PER_STOP = 8  # cap to avoid bloating the narrator prompt


def retriever(state: TourState) -> TourState:
    """
    Real retriever node.
    For each selected stop, queries ChromaDB with the stop's keywords
    and populates stop.chunks with the top relevant chunks.
    """
    print(f"[retriever] Retrieving chunks for {len(state.selected_stops)} stops.")

    for stop in state.selected_stops:
        print(f"[retriever] Querying for: {stop.name}")

        seen_chunk_ids = set()  # deduplicate chunks across keyword queries
        chunks = []

        for keyword in stop.keywords:
            results = query_chunks(
                query_text=keyword,
                site_id=state.site_id,
                n_results=CHUNKS_PER_KEYWORD,
            )

            for chunk in results:
                if chunk["chunk_id"] not in seen_chunk_ids:
                    seen_chunk_ids.add(chunk["chunk_id"])
                    chunks.append(chunk)

        # Cap total chunks per stop
        stop.chunks = chunks[:MAX_CHUNKS_PER_STOP]
        print(f"[retriever] ✓ {stop.name} — {len(stop.chunks)} chunks retrieved.")

    print(f"[retriever] Retrieval complete.")
    return state
