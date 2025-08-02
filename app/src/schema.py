from typing import List, Dict, Optional

# --- Data Schema ---
# This defines the schema for our events (compatible with Python 3.6)
# Using Dict instead of TypedDict for Python 3.6 compatibility
MusicEvent = Dict[str, any]

# For reference, the expected structure is:
# {
#     "id": str,
#     "name": str, 
#     "artists": List[str],
#     "venue": str,
#     "city": str,
#     "country": str,
#     "date": str  # ISO 8601 format: "YYYY-MM-DDTHH:MM:SSZ"
# } 