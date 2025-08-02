import json
import logging
from typing import List

from src.schema import MusicEvent
from src.config import SAVE_TO_MEILISEARCH, MEILI_URL, MEILI_MASTER_KEY, OUTPUT_FILE

if SAVE_TO_MEILISEARCH:
    try:
        import meilisearch
    except ImportError:
        print("meilisearch-python-sdk is not installed. Please install it with 'pip install meilisearch'")
        SAVE_TO_MEILISEARCH = False

def save_to_file(events: List[MusicEvent]):
    """Saves the list of events to a local JSON file."""
    logging.info(f"Saving {len(events)} events to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def save_to_meilisearch(events: List[MusicEvent]):
    """Saves the list of events to a MeiliSearch instance."""
    if not SAVE_TO_MEILISEARCH:
        logging.info("Skipping save to MeiliSearch (feature flag is off).")
        return

    logging.info(f"Saving {len(events)} events to MeiliSearch at {MEILI_URL}")
    try:
        client = meilisearch.Client(MEILI_URL, MEILI_MASTER_KEY)
        index = client.index("events")
        index.add_documents(events, primary_key='id')
    except Exception as e:
        logging.error(f"Failed to save events to MeiliSearch: {e}") 