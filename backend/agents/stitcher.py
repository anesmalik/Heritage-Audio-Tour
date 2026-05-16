"""
stitcher.py — Real implementation of the stitcher node.

Responsibility: Assemble the ordered stop narrations into a single
final script and generate a GeoJSON FeatureCollection from the
ordered stop coordinates.

This node has NO LLM call — it's pure string formatting and
data structure assembly.

Output:
    state.final_script  — complete narration script as a string
    state.geojson_route — GeoJSON FeatureCollection for map display
"""

from backend.agents.state import TourState, Stop


# ------------------------------------------------------------------ #
# Script templates
# ------------------------------------------------------------------ #
INTRO_TEMPLATE = """Welcome to your {duration}-minute audio tour of {site_name}.
Today you will visit {stop_count} remarkable stops across one of the world's most
significant heritage sites. Please follow the route on your map and begin at your
first stop when you are ready.

---
"""

OUTRO_TEMPLATE = """
---

Thank you for joining this audio tour of {site_name}. You have visited {stop_count} stops
and traveled through thousands of years of human history. We hope this experience
has deepened your appreciation of Iraq's extraordinary cultural heritage.
"""

STOP_TEMPLATE = """## Stop {number}: {name}

{narration}

---
"""


def _build_script(state: TourState) -> str:
    """
    Assemble the final narration script from ordered stops.
    Includes intro, all stop narrations with headers, and outro.
    """
    # Build site name from site_id for display
    site_name = state.site_id.replace("_", " ").title()

    intro = INTRO_TEMPLATE.format(
        duration=state.duration_mins,
        site_name=site_name,
        stop_count=len(state.ordered_stops),
    )

    stops_text = ""
    for i, stop in enumerate(state.ordered_stops, 1):
        # Strip citation tags from final script — they're internal,
        # not meant for the visitor's ears
        clean_narration = _strip_citations(stop.narration or "")
        stops_text += STOP_TEMPLATE.format(
            number=i,
            name=stop.name,
            narration=clean_narration,
        )

    outro = OUTRO_TEMPLATE.format(
        site_name=site_name,
        stop_count=len(state.ordered_stops),
    )

    return intro + stops_text + outro


def _strip_citations(text: str) -> str:
    """
    Remove [chunk_id] citation tags from narration text.
    These are internal verification markers — not for visitors.
    """
    import re
    return re.sub(r"\[[a-z0-9_]+\]", "", text).strip()


def _build_geojson(state: TourState) -> dict:
    """
    Build a GeoJSON FeatureCollection from ordered stop coordinates.
    Includes:
        - A Point feature for each stop
        - A LineString feature connecting all stops in order (the route)
    """
    features = []

    # Point features — one per stop
    for i, stop in enumerate(state.ordered_stops, 1):
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": stop.coordinates,  # [longitude, latitude]
            },
            "properties": {
                "stop_number": i,
                "id":          stop.id,
                "name":        stop.name,
                "description": stop.description,
            }
        })

    # LineString feature — the walking route connecting all stops
    route_coordinates = [stop.coordinates for stop in state.ordered_stops]
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": route_coordinates,
        },
        "properties": {
            "type":       "route",
            "site_id":    state.site_id,
            "duration":   state.duration_mins,
            "stop_count": len(state.ordered_stops),
        }
    })

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def stitcher(state: TourState) -> TourState:
    """
    Real stitcher node.
    Assembles final_script and geojson_route from ordered stops.
    """
    print(f"[stitcher] Stitching script for {len(state.ordered_stops)} stops.")

    if not state.ordered_stops:
        print(f"[stitcher] WARNING: No ordered stops to stitch.")
        return state

    # Build final script
    state.final_script = _build_script(state)
    word_count = len(state.final_script.split())
    print(f"[stitcher] ✓ Script assembled — {word_count} total words.")

    # Build GeoJSON route
    state.geojson_route = _build_geojson(state)
    point_count = len([f for f in state.geojson_route["features"] if f["geometry"]["type"] == "Point"])
    print(f"[stitcher] ✓ GeoJSON route built — {point_count} stops + 1 LineString.")

    return state
