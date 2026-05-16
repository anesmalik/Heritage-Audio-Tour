"""
narrator.py — Real implementation of the narrator node.

Responsibility: For each selected stop, send its retrieved chunks
to the LLM and generate engaging audio tour narration.

Key constraint: Every factual claim MUST be grounded in a provided
chunk. The LLM is explicitly forbidden from using outside knowledge.
This is the primary anti-hallucination guardrail.

Citation format: The narrator wraps each claim in [chunk_id] tags
so the verifier can trace every fact back to its source chunk.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

from backend.agents.state import TourState, Stop

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an expert heritage audio tour narrator specializing in Iraqi archaeological sites.
You write engaging, vivid narration for visitors standing at a specific location.

STRICT RULES — violations will cause the tour to fail verification:
1. Every factual claim MUST come from the provided source chunks only.
2. You MUST cite each claim using the format [chunk_id] immediately after the claim.
3. You MUST NOT use any outside knowledge, even if you are certain it is correct.
4. If the chunks do not contain enough information for a claim, omit that claim entirely.
5. Write in second person ("You are standing...", "Before you...").
6. Keep narration between 150-250 words — this is audio, not an essay.
7. End with a transition sentence to prepare the visitor to move to the next stop.
8. Your response must never exceed 1500 characters total.

Citation example:
"The gate was built by Nebuchadnezzar II around 575 BC [babylon__history__2]. 
It was dedicated to the goddess Ishtar [babylon__ishtar_gate__0]."
"""


def _build_chunks_context(stop: Stop) -> str:
    """Format the stop's chunks into a readable context block for the LLM."""
    if not stop.chunks:
        return "No source chunks available for this stop."

    lines = []
    for chunk in stop.chunks:
        lines.append(f"[{chunk['chunk_id']}]\n{chunk['text']}\n")
    return "\n---\n".join(lines)


def _build_user_prompt(stop: Stop) -> str:
    """Build the narration prompt for a single stop."""
    chunks_context = _build_chunks_context(stop)
    return f"""Write audio tour narration for this stop.

Stop name: {stop.name}
Stop description: {stop.description}

SOURCE CHUNKS (use ONLY these for facts — cite each one with [chunk_id]):
{chunks_context}

Write the narration now. Remember: cite every fact, 150-250 words, second person, end with transition."""


def narrate_stop(stop: Stop) -> Stop:
    """
    Generate narration for a single stop.
    Returns the stop with stop.narration populated.
    """
    print(f"[narrator] Writing narration for: {stop.name}")

    if not stop.chunks:
        print(f"[narrator] WARNING: No chunks for {stop.name} — skipping narration.")
        stop.narration = f"Welcome to {stop.name}. {stop.description}"
        return stop

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _build_user_prompt(stop)},
        ],
        temperature=0.7,   # slightly higher for more engaging prose
        max_tokens=400,
    )

    stop.narration = response.choices[0].message.content.strip()
    word_count = len(stop.narration.split())
    print(f"[narrator] ✓ {stop.name} — {word_count} words written.")
    return stop


def narrator(state: TourState) -> TourState:
    """
    Real narrator node.
    Iterates through all selected stops and generates cited narration
    for each one using its retrieved chunks.
    """
    print(f"[narrator] Writing narration for {len(state.selected_stops)} stops.")

    for i, stop in enumerate(state.selected_stops):
        if state.selected_stops[i].verified:
            print(f"[narrator] Skipping {stop.name} — already verified.")
            continue
        state.selected_stops[i] = narrate_stop(stop)

    print(f"[narrator] Narration complete for all stops.")
    return state
