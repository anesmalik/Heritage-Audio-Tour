"""
stop_selector.py — Real implementation of the stop selector node.

Responsibility: Load the site YAML, call the LLM to select the best
subset of stops for the requested duration, and populate
state.selected_stops with fully constructed Stop objects.

Duration → stop count:
    30 mins → 4 stops
    60 mins → 6 stops
    90 mins → 8 stops
"""

import os
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from backend.agents.state import TourState, Stop

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------------------------ #
# Constants
# ------------------------------------------------------------------ #
SITES_DIR    = Path("backend/sites")
DURATION_MAP = {30: 4, 60: 6, 90: 8}

SYSTEM_PROMPT = """You are an expert heritage tour curator specializing in Iraqi archaeological sites.
Your job is to select the best stops for a visitor tour based on the available candidates and duration.

You must respond ONLY with a valid JSON array. No preamble, no markdown, no explanation outside the JSON.

Each item in the array must have exactly these fields:
{
    "id": "<stop id from the candidates>",
    "justification": "<one sentence explaining why this stop was chosen for this duration>"
}

Selection criteria:
- Prioritize stops with the highest historical significance
- Ensure thematic variety (religious, royal, civic, archaeological)
- For shorter tours, pick the most iconic and accessible stops
- Never invent stops — only use IDs from the provided candidate list
"""


def _load_site_yaml(site_id: str) -> dict:
    """Load and parse the site YAML file."""
    path = SITES_DIR / f"{site_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Site YAML not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_user_prompt(site_data: dict, n_stops: int) -> str:
    """Build the user prompt with candidate stops."""
    candidates_text = "\n".join([
        f"- id: {s['id']}\n  name: {s['name']}\n  description: {s['description']}"
        for s in site_data["stops"]
    ])
    return f"""Site: {site_data['site_name']} ({site_data['country']})
Tour duration: {n_stops} stops needed

Candidate stops:
{candidates_text}

Select exactly {n_stops} stops from the candidates above.
Return a JSON array with {n_stops} items."""


def stop_selector(state: TourState) -> TourState:
    """
    Real stop selector node.
    Loads the site YAML, calls the LLM to select stops, and
    populates state.selected_stops with Stop objects.
    """
    print(f"[stop_selector] site={state.site_id} duration={state.duration_mins}mins")

    # Determine how many stops to select
    n_stops = DURATION_MAP.get(state.duration_mins, 6)

    # Load site YAML
    try:
        site_data = _load_site_yaml(state.site_id)
    except FileNotFoundError as e:
        print(f"[stop_selector] ERROR: {e}")
        state.error = str(e)
        return state

    # Build a lookup map for stop data by id
    stop_lookup = {s["id"]: s for s in site_data["stops"]}

    # Call the LLM
    print(f"[stop_selector] Calling LLM to select {n_stops} stops...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _build_user_prompt(site_data, n_stops)},
        ],
        temperature=0.3,   # low temperature = more consistent curation decisions
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    # Parse the JSON response
    try:
        parsed = json.loads(raw)
        # Handle both {"stops": [...]} and plain [...] responses
        selections = parsed if isinstance(parsed, list) else next(iter(parsed.values()))
    except (json.JSONDecodeError, StopIteration) as e:
        print(f"[stop_selector] ERROR parsing LLM response: {e}")
        state.error = f"stop_selector JSON parse error: {e}"
        return state

    # Build Stop objects from selections
    selected_stops = []
    for item in selections:
        stop_id = item.get("id")
        if stop_id not in stop_lookup:
            print(f"[stop_selector] WARNING: LLM returned unknown stop id '{stop_id}' — skipping.")
            continue

        yaml_stop = stop_lookup[stop_id]
        stop = Stop(
            id=          yaml_stop["id"],
            name=        yaml_stop["name"],
            coordinates= yaml_stop["coordinates"],
            keywords=    yaml_stop["keywords"],
            description= yaml_stop["description"],
        )
        selected_stops.append(stop)
        print(f"[stop_selector] ✓ {stop.name} — {item.get('justification', '')}")

    state.selected_stops = selected_stops
    print(f"[stop_selector] Selected {len(selected_stops)} stops.")
    return state
