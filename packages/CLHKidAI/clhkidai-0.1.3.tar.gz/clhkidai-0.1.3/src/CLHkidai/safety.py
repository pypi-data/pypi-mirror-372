from __future__ import annotations
from typing import Iterable

# Super-simple, classroom-visible filter you can discuss with kids.
_DEFAULT_BLOCKLIST: set[str] = {
    "violence", "weapon", "drugs", "hate", "self-harm",
    # add/remove based on your school policy
}

def is_allowed(text: str, extra_blocklist: Iterable[str] | None = None) -> bool:
    text_low = (text or "").lower()
    blocklist = set(_DEFAULT_BLOCKLIST)
    if extra_blocklist:
        blocklist |= set(w.lower() for w in extra_blocklist)
    return not any(bad in text_low for bad in blocklist)
