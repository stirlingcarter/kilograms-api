import logging
import meilisearch
from typing import List
from src.schema import MusicEvent

def save_events_to_meilisearch(events: List[MusicEvent], meili_client) -> bool:
    """
    Save events to Meilisearch index.
    
    Args:
        events: List of normalized events to save
        meili_client: Meilisearch client instance
        
    Returns:
        True if successful, False otherwise
    """
    if not events:
        logging.info("No events to save")
        return True
        
    try:
        logging.info(f"Saving {len(events)} events to Meilisearch")
        index = meili_client.index("events")
        index.add_documents(events, primary_key='id')
        logging.info("Successfully saved events to Meilisearch")
        return True
    except Exception as e:
        logging.error(f"Failed to save events to Meilisearch: {e}")
        return False 