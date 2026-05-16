"""
chroma_store.py — ChromaDB read/write interface.

Responsibility: All ChromaDB operations live here. The rest of the
codebase never imports chromadb directly — it always goes through
this module. This makes swapping vector stores a one-file change.
"""

import chromadb
from chromadb.config import Settings


# ------------------------------------------------------------------ #
# ChromaDB client — persistent local storage in backend/corpus/db/
# ------------------------------------------------------------------ #
CHROMA_PATH = "backend/corpus/db"
COLLECTION_NAME = "iraqi_heritage"


def get_collection():
    """
    Return the ChromaDB collection, creating it if it doesn't exist.
    Uses persistent local storage so the index survives restarts.
    """
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )
    return collection


def store_chunks(chunks: list[dict]) -> None:
    """
    Embed and store a list of Chunk dicts into ChromaDB.

    ChromaDB handles embedding internally using its default
    embedding function (all-MiniLM-L6-v2 via sentence-transformers).
    We pass text — ChromaDB converts to vectors automatically.

    Args:
        chunks: List of Chunk dicts from chunker.chunk_sections().
    """
    if not chunks:
        print("[chroma_store] No chunks to store.")
        return

    collection = get_collection()

    # ChromaDB expects parallel lists for ids, documents, and metadatas
    ids        = [c["chunk_id"]   for c in chunks]
    documents  = [c["text"]       for c in chunks]
    metadatas  = [
        {
            "site_id":    c["site_id"],
            "section":    c["section"],
            "source_url": c["source_url"],
        }
        for c in chunks
    ]

    # upsert = insert if new, update if chunk_id already exists.
    # Safe to re-run ingest without duplicating chunks.
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"[chroma_store] Stored {len(chunks)} chunks.")


def query_chunks(query_text: str, site_id: str, n_results: int = 5) -> list[dict]:
    """
    Retrieve the most relevant chunks for a query string.

    Filters by site_id so Babylon queries never return Ur chunks.

    Args:
        query_text: The search query (e.g. keywords from the YAML stop).
        site_id:    Filter results to this site only.
        n_results:  How many chunks to return (default 5).

    Returns:
        A list of dicts with chunk_id, text, source_url, and score.
    """
    collection = get_collection()

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"site_id": site_id},  # metadata filter — site isolation
        include=["documents", "metadatas", "distances"],
    )

    # Unpack ChromaDB's parallel list structure into clean dicts
    chunks = []
    for i, chunk_id in enumerate(results["ids"][0]):
        chunks.append({
            "chunk_id":   chunk_id,
            "text":       results["documents"][0][i],
            "source_url": results["metadatas"][0][i]["source_url"],
            "section":    results["metadatas"][0][i]["section"],
            "score":      1 - results["distances"][0][i],  # cosine: 1=identical, 0=unrelated
        })

    return chunks


def site_exists(site_id: str) -> bool:
    """
    Check if a site has already been ingested.
    Used by ingest.py to skip re-ingesting sites that are already in the DB.
    """
    collection = get_collection()
    results = collection.get(where={"site_id": site_id}, limit=1)
    return len(results["ids"]) > 0


# ------------------------------------------------------------------ #
# Smoke test:
#   python chroma_store.py
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    # Store a fake chunk and retrieve it
    fake_chunks = [
        {
            "chunk_id":   "babylon__history__0",
            "text":       "Babylon was the capital of the Neo-Babylonian Empire. "
                          "Nebuchadnezzar II rebuilt the city and constructed the Ishtar Gate.",
            "site_id":    "babylon",
            "section":    "History",
            "source_url": "https://en.wikipedia.org/wiki/Babylon",
        }
    ]

    store_chunks(fake_chunks)

    results = query_chunks("Ishtar Gate Nebuchadnezzar", site_id="babylon")
    for r in results:
        print(f"\nchunk_id : {r['chunk_id']}")
        print(f"score    : {r['score']:.3f}")
        print(f"text     : {r['text'][:150]}")
