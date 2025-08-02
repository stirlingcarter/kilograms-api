from typing import List, TypedDict, Optional

# --- Data Schema ---
# This TypedDict defines the rigid schema for our events.
class MusicEvent(TypedDict):
    id: str
    name: str
    artists: List[str]
    venue: str
    city: str
    country: str
    date: str  # ISO 8601 format: "YYYY-MM-DDTHH:MM:SSZ" 