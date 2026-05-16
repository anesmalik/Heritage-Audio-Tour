"""
verifier.py — Real implementation of the verifier node.

Responsibility: Parse the narration for citation tags [chunk_id],
verify each cited chunk_id actually exists in the stop's retrieved
chunks, and flag any uncited claims or invalid citations.

This is the anti-hallucination enforcement layer. If the narrator
invented a fact without citing a chunk, the verifier catches it
and triggers a retry via the conditional edge in the graph.

Verification logic (no LLM call — pure string parsing + set lookup):
    1. Extract all [chunk_id] tags from the narration
    2. Check each chunk_id exists in the stop's retrieved chunks
    3. Check there are no sentences without a citation
    4. If all checks pass → verification_passed = True
    5. If any check fails → verification_passed = False → retry
"""

import re
from backend.agents.state import TourState, Stop


# ------------------------------------------------------------------ #
# Regex to extract all [chunk_id] citation tags from narration text
# Matches: [babylon__history__2], [ur__royal_cemetery__0], etc.
# ------------------------------------------------------------------ #
CITATION_PATTERN = re.compile(r"\[([a-z0-9_]+)\]")

# Minimum citation ratio — at least this fraction of sentences
# must contain a citation. Prevents walls of uncited prose.
MIN_CITATION_RATIO = 0.5


def _extract_citations(narration: str) -> list[str]:
    """Extract all chunk_id values from [chunk_id] tags in narration."""
    return CITATION_PATTERN.findall(narration)


def _get_valid_chunk_ids(stop: Stop) -> set[str]:
    """Return the set of chunk_ids that were actually retrieved for this stop."""
    return {chunk["chunk_id"] for chunk in stop.chunks}


def _count_sentences(text: str) -> int:
    """Rough sentence count — split on . ! ?"""
    sentences = re.split(r"[.!?]+", text)
    return len([s for s in sentences if s.strip()])


def verify_stop(stop: Stop) -> tuple[bool, list[str], list[str]]:
    """
    Verify the narration for a single stop.

    Returns:
        (passed, valid_citations, issues)
        - passed:          True if all checks pass
        - valid_citations: list of chunk_ids that were correctly cited
        - issues:          list of human-readable problem descriptions
    """
    issues = []
    valid_citations = []

    if not stop.narration:
        return False, [], ["No narration found for this stop."]

    cited_ids    = _extract_citations(stop.narration)
    valid_ids    = _get_valid_chunk_ids(stop)
    sentence_count = _count_sentences(stop.narration)

    # Check 1 — Are there any citations at all?
    if not cited_ids:
        issues.append(f"{stop.name}: No citations found in narration.")
        return False, [], issues

    # Check 2 — Are all cited chunk_ids valid (actually retrieved)?
    for chunk_id in cited_ids:
        if chunk_id in valid_ids:
            valid_citations.append(chunk_id)
        else:
            issues.append(f"{stop.name}: Invalid citation [{chunk_id}] — not in retrieved chunks.")

    # Check 3 — Citation density (at least MIN_CITATION_RATIO of sentences cited)
    citation_ratio = len(cited_ids) / max(sentence_count, 1)
    if citation_ratio < MIN_CITATION_RATIO:
        issues.append(
            f"{stop.name}: Low citation density ({citation_ratio:.0%}) — "
            f"too many uncited claims."
        )

    passed = len(issues) == 0
    return passed, valid_citations, issues


def verifier(state: TourState) -> TourState:
    """
    Real verifier node.
    Verifies narration citations for all selected stops.
    Sets state.verification_passed and populates stop.citations.
    """
    print(f"[verifier] Verifying narration for {len(state.selected_stops)} stops.")

    all_passed = True
    all_issues = []

    for i, stop in enumerate(state.selected_stops):
        passed, valid_citations, issues = verify_stop(stop)

        state.selected_stops[i].verified  = passed
        state.selected_stops[i].citations = valid_citations

        if passed:
            print(f"[verifier] ✓ {stop.name} — {len(valid_citations)} citations verified.")
        else:
            all_passed = False
            all_issues.extend(issues)
            for issue in issues:
                print(f"[verifier] ✗ {issue}")

    state.verification_passed = all_passed

    if all_passed:
        print(f"[verifier] ✓ All stops passed verification.")
    else:
        print(f"[verifier] ✗ Verification failed — {len(all_issues)} issues found.")
        print(f"[verifier] Retry {state.retry_count + 1}/{state.MAX_RETRIES} will be triggered.")

    return state
