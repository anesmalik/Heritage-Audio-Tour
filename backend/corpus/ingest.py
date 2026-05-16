"""
ingest.py — One-time corpus ingestion script.

Responsibility: Orchestrate the full ingest pipeline for all three sites:
    1. Scrape Wikipedia (EN + AR) for each site
    2. Translate Arabic sections to English
    3. Chunk all sections
    4. Store chunks in ChromaDB

Run this once before starting the agent pipeline:
    python -m backend.corpus.ingest

Re-running is safe — upsert prevents duplicate chunks.
"""

import yaml
from pathlib import Path
import requests

from backend.corpus.scraper import scrape_article
from backend.corpus.chunker import chunk_sections
from backend.corpus.chroma_store import store_chunks, site_exists


# ------------------------------------------------------------------ #
# Site config — maps site_id to Wikipedia page titles (EN + AR)
# ------------------------------------------------------------------ #
SITES = {
    "babylon": {
        "en": ["Babylon", "Ishtar Gate", "Etemenanki"],
        "ar": ["بابل", "بوابة عشتار"],
    },
    "ur": {
        "en": ["Ur", "Royal Cemetery of Ur", "Great Ziggurat of Ur"],
        "ar": ["أور", "زقورة أور"],
    },
    "erbil_citadel": {
        "en": ["Erbil Citadel", "Erbil", "Qaysari Bazaar"],
        "ar": ["قلعة أربيل", "أربيل"],
    },
}

SITES_DIR = Path("backend/sites")


# ------------------------------------------------------------------ #
# Translation
# ------------------------------------------------------------------ #

def translate_sections(sections: list[dict]) -> list[dict]:
    translated = []
    for section in sections:
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "ar",
                "tl": "en",
                "dt": "t",
                "q": section["text"]
            }
            response = requests.get(url, params=params)
            result = response.json()
            translated_text = "".join([item[0] for item in result[0] if item[0]])

            params["q"] = section["title"]
            response = requests.get(url, params=params)
            result = response.json()
            translated_title = "".join([item[0] for item in result[0] if item[0]])

            translated.append({
                "title":      translated_title,
                "text":       translated_text,
                "source_url": section["source_url"],
            })
        except Exception as e:
            print(f"[ingest] Translation failed for '{section['title']}': {e}")
            continue
    return translated


# ------------------------------------------------------------------ #
# Per-site ingestion
# ------------------------------------------------------------------ #
def ingest_site(site_id: str, config: dict) -> None:
    """
    Run the full ingest pipeline for a single site.

    Args:
        site_id: e.g. "babylon"
        config:  Dict with "en" and "ar" lists of Wikipedia page titles.
    """
    print(f"\n{'='*50}")
    print(f"[ingest] Starting site: {site_id}")
    print(f"{'='*50}")

    if site_exists(site_id):
        print(f"[ingest] '{site_id}' already in ChromaDB — skipping.")
        print(f"[ingest] To re-ingest, delete backend/corpus/db/ and re-run.")
        return

    all_chunks = []

    # ── English articles ──────────────────────────────────────────── #
    for page_title in config["en"]:
        sections = scrape_article(page_title, language="en")
        chunks   = chunk_sections(sections, site_id=site_id)
        all_chunks.extend(chunks)

    # ── Arabic articles (scrape → translate → chunk) ──────────────── #
    for page_title in config["ar"]:
        sections   = scrape_article(page_title, language="ar")
        translated = translate_sections(sections)
        chunks     = chunk_sections(translated, site_id=site_id)
        all_chunks.extend(chunks)

    # ── Store everything in ChromaDB ──────────────────────────────── #
    store_chunks(all_chunks)
    print(f"[ingest] ✓ '{site_id}' complete — {len(all_chunks)} total chunks stored.")


# ------------------------------------------------------------------ #
# Main entry point
# ------------------------------------------------------------------ #
def main():
    print("\n[ingest] Iraqi Heritage Tour — Corpus Ingestion")
    print("[ingest] This runs once to build the ChromaDB knowledge base.\n")

    for site_id, config in SITES.items():
        ingest_site(site_id, config)

    print("\n[ingest] ✓ All sites ingested. ChromaDB is ready.")
    print("[ingest] Index location: backend/corpus/db/")


if __name__ == "__main__":
    main()
