"""
scraper.py — Wikipedia article fetcher and section extractor.

Responsibility: Given a Wikipedia page title, return a list of clean
sections (title + text + source URL). Skips non-prose sections like
References, See also, and External links.

This module has no knowledge of ChromaDB, chunking, or embeddings.
It does one thing: fetch and clean Wikipedia content.
"""

import wikipediaapi

# ------------------------------------------------------------------ #
# Blocklist — section titles we never want as corpus chunks.
# These contain no useful prose for narration.
# ------------------------------------------------------------------ #
BLOCKLISTED_SECTIONS = {
    "references",
    "see also",
    "external links",
    "notes",
    "bibliography",
    "further reading",
    "footnotes",
    "sources",
    "citations",
}


def _is_blocked(title: str) -> bool:
    """Return True if a section title is on the blocklist."""
    return title.strip().lower() in BLOCKLISTED_SECTIONS


def _extract_sections(section, source_url: str, results: list) -> None:
    """
    Recursively walk a wikipediaapi Section object and its children.
    Appends valid sections to the results list in-place.

    We recurse because Wikipedia articles have nested sections:
        == History ==          <- top-level section
            === Early period === <- subsection (also useful prose)
            === Later period ===
        == Architecture ==
    """
    # Skip empty sections and blocklisted ones
    if not section.text.strip():
        return
    if _is_blocked(section.title):
        return

    results.append({
        "title": section.title.strip(),
        "text": section.text.strip(),
        "source_url": source_url,
    })

    # Recurse into any subsections
    for subsection in section.sections:
        _extract_sections(subsection, source_url, results)


def scrape_article(page_title: str, language: str = "en") -> list[dict]:
    """
    Fetch a Wikipedia article by title and return its sections.

    Args:
        page_title: The Wikipedia page title, e.g. "Babylon" or "أور" (Arabic).
        language:   Wikipedia language code — "en" for English, "ar" for Arabic.

    Returns:
        A list of dicts, each with keys:
            - title      (str): Section heading
            - text       (str): Section prose
            - source_url (str): Full Wikipedia URL for citation tracking

    Returns an empty list if the page does not exist.
    """
    # Initialize the Wikipedia API client.
    # user_agent is required by Wikipedia's API policy — identify your app.
    wiki = wikipediaapi.Wikipedia(
        language=language,
        user_agent="IraqiHeritageTour/1.0 (portfolio project)"
    )

    page = wiki.page(page_title)

    if not page.exists():
        print(f"[scraper] WARNING: Page '{page_title}' not found in '{language}' Wikipedia.")
        return []

    source_url = page.fullurl
    sections = []

    # Walk all top-level sections (each recurses into its own subsections)
    for section in page.sections:
        _extract_sections(section, source_url, sections)

    print(f"[scraper] Fetched '{page_title}' ({language}): {len(sections)} sections.")
    return sections


# ------------------------------------------------------------------ #
# Quick smoke test — run this file directly to verify it works:
#   python scraper.py
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    results = scrape_article("Babylon", language="en")
    for r in results[:3]:  # Print first 3 sections as a sanity check
        print(f"\n--- {r['title']} ---")
        print(r['text'][:300])  # First 300 chars of each section
        print(f"Source: {r['source_url']}")
