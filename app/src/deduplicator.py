from typing import List, Set
from src.schema import MusicEvent

def deduplicate_events(events: List[MusicEvent]) -> List[MusicEvent]:
    """
    Deduplicates a list of events.

    An event is considered a duplicate if it has the same artists performing
    at roughly the same time. "Roughly" is defined as being on the same day.
    """
    seen_events: Set[str] = set()
    deduplicated = []
    for event in events:
        # Normalize date to just the day for deduplication
        event_day = event['date'].split('T')[0]
        # Sort artists to ensure order doesn't matter
        sorted_artists = tuple(sorted(artist.lower() for artist in event['artists']))
        
        # Create a unique key for the event
        event_key = f"{event_day}-{sorted_artists}"

        if event_key not in seen_events:
            seen_events.add(event_key)
            deduplicated.append(event)
    return deduplicated 