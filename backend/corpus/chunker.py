"""
chunker.py — Turns raw Wikipedia sections into Chunk objects.

Responsibility: Take the list of sections from scraper.py and produce
a list of Chunk dicts with stable IDs, clean text, and metadata.

A Chunk is the atomic unit stored in ChromaDB. Every downstream
agent works with chunks — not raw Wikipedia sections.
"""

import re


# ------------------------------------------------------------------ #
# Minimum character length for a chunk to be considered useful.
# Sections shorter than this are likely stubs and add noise.
# ------------------------------------------------------------------ #
MIN_CHUNK_LENGTH = 100


def _make_chunk_id(site_id: str, section_title: str, index: int) -> str:
    """
    Build a stable, human-readable chunk ID.

    Format: {site_id}__{section_slug}__{index}
    Example: babylon__history__0
             ur__royal_cemetery__2

    We slugify the section title (lowercase, spaces to underscores,
    remove special characters) so IDs are safe for ChromaDB keys.
    """
    slug = section_title.lower().strip()
    slug = re.sub(r"[^\w\s]", "", slug)   # remove punctuation
    slug = re.sub(r"\s+", "_", slug)       # spaces to underscores
    return f"{site_id}__{slug}__{index}"


def _clean_text(text: str) -> str:
    """
    Light cleaning of Wikipedia section text.
    - Collapse multiple blank lines into one
    - Strip leading/trailing whitespace
    We deliberately avoid aggressive cleaning — the verifier needs
    to match claim text back to this content.
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_sections(sections: list[dict], site_id: str) -> list[dict]:
    """
    Convert a list of scraped sections into a list of Chunk dicts.

    Args:
        sections: Output from scraper.scrape_article() — list of
                  {title, text, source_url} dicts.
        site_id:  The site identifier (e.g. "babylon", "ur").
                  Used to namespace chunk IDs and filter at retrieval.

    Returns:
        A list of Chunk dicts, each with:
            - chunk_id   (str): Stable unique identifier
            - text       (str): Cleaned section prose
            - source_url (str): Wikipedia URL for citation
            - site_id    (str): Which site this chunk belongs to
            - section    (str): Human-readable section title
    """
    chunks = []

    for index, section in enumerate(sections):
        text = _clean_text(section["text"])

        # Skip sections that are too short to be useful
        if len(text) < MIN_CHUNK_LENGTH:
            continue

        chunk_id = _make_chunk_id(site_id, section["title"], index)

        chunks.append({
            "chunk_id":   chunk_id,
            "text":       text,
            "source_url": section["source_url"],
            "site_id":    site_id,
            "section":    section["title"],
        })

    print(f"[chunker] site='{site_id}': {len(sections)} sections → {len(chunks)} chunks.")
    return chunks


# ------------------------------------------------------------------ #
# Smoke test — run directly to verify chunking works:
#   python chunker.py
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    # Simulate what scraper.py would return
    fake_sections = [
        {
            "title": "History",
            "text": "Babylon was one of the most important cities in ancient Mesopotamia. "
                    "It served as the capital of the Babylonian Empire under Nebuchadnezzar II.",
            "source_url": "https://en.wikipedia.org/wiki/Babylon",
        },
        {
            "title": "Stub",
            "text": "Short.",  # Should be filtered out
            "source_url": "https://en.wikipedia.org/wiki/Babylon",
        },
    ]

    chunks = chunk_sections(fake_sections, site_id="babylon")
    for c in chunks:
        print(f"\nchunk_id : {c['chunk_id']}")
        print(f"section  : {c['section']}")
        print(f"text     : {c['text'][:100]}...")
