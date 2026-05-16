"""
router.py — Real implementation of the router node.

Responsibility: Order the selected stops into the most logical
walking sequence using a nearest-neighbor algorithm on coordinates.

This node has NO LLM call — it's pure mathematics.
Input:  state.selected_stops (unordered)
Output: state.ordered_stops  (ordered by proximity)

Algorithm: Nearest-neighbor greedy TSP approximation
    1. Start from the first stop (index 0)
    2. At each step, find the unvisited stop closest to the current one
    3. Move to that stop and repeat until all stops are visited

This is O(n²) which is perfectly fine for n ≤ 8 stops.
"""

import math
from backend.agents.state import TourState, Stop


def _haversine_distance(coord1: list[float], coord2: list[float]) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    Uses the Haversine formula — accurate for short distances.

    Args:
        coord1: [longitude, latitude] in decimal degrees
        coord2: [longitude, latitude] in decimal degrees

    Returns:
        Distance in kilometers.
    """
    # Earth's radius in kilometers
    R = 6371.0

    # Coordinates are stored as [longitude, latitude] (GeoJSON order)
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    # Convert to radians
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    lon1, lon2 = math.radians(lon1), math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def _nearest_neighbor_sort(stops: list[Stop]) -> list[Stop]:
    """
    Sort stops into a walking-friendly sequence using nearest-neighbor.

    Starts from the first stop and greedily visits the closest
    unvisited stop at each step.
    """
    if len(stops) <= 1:
        return stops

    unvisited = list(stops)
    ordered   = [unvisited.pop(0)]  # start from the first stop

    while unvisited:
        current = ordered[-1]
        # Find the closest unvisited stop to the current one
        closest = min(
            unvisited,
            key=lambda s: _haversine_distance(current.coordinates, s.coordinates)
        )
        ordered.append(closest)
        unvisited.remove(closest)

    return ordered


def router(state: TourState) -> TourState:
    """
    Real router node.
    Orders selected stops by geographic proximity using
    nearest-neighbor algorithm on their coordinates.
    Populates state.ordered_stops.
    """
    print(f"[router] Ordering {len(state.selected_stops)} stops by proximity.")

    if not state.selected_stops:
        print(f"[router] WARNING: No stops to order.")
        state.ordered_stops = []
        return state

    ordered = _nearest_neighbor_sort(state.selected_stops)
    state.ordered_stops = ordered

    # Log the final sequence
    print(f"[router] ✓ Optimized walking route:")
    for i, stop in enumerate(ordered, 1):
        print(f"[router]   {i}. {stop.name} {stop.coordinates}")

    return state
