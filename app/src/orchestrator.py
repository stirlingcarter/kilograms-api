import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List

from src.scrapers.nineteen_hz import get_19hz_events
from src.normalizer import normalize_ra_event
from src.deduplicator import deduplicate_events
from src.schema import MusicEvent

# Define all the cities we want to scrape
CITIES = ["sf", "la", "seattle", "atlanta", "miami", "dc", "chicago", "detroit", "denver", "vegas", "portland"]

def scrape_city_events(city: str) -> List[MusicEvent]:
    """Scrape events for a single city and return normalized events."""
    try:
        logging.info(f"Scraping events for {city}")
        raw_events = get_19hz_events(city)
        
        # Normalize all events
        normalized_events = []
        for event in raw_events:
            normalized = normalize_ra_event(event)
            if normalized:
                normalized_events.append(normalized)
        
        logging.info(f"Found {len(normalized_events)} events for {city}")
        return normalized_events
    except Exception as e:
        logging.error(f"Error scraping {city}: {e}")
        return []

def refresh_all_events() -> dict:
    """
    Orchestrates the complete event refresh process:
    1. Scrape all cities in parallel
    2. Deduplicate events
    3. Return summary statistics
    """
    logging.info("Starting events refresh for all cities")
    
    # Use ThreadPoolExecutor to scrape all cities in parallel
    all_events = []
    with ThreadPoolExecutor(max_workers=len(CITIES)) as executor:
        # Submit all scraping tasks
        future_to_city = {executor.submit(scrape_city_events, city): city for city in CITIES}
        
        # Collect results as they complete
        for future in future_to_city:
            city = future_to_city[future]
            try:
                city_events = future.result()
                all_events.extend(city_events)
            except Exception as e:
                logging.error(f"Failed to scrape {city}: {e}")
    
    # Deduplicate events
    logging.info(f"Deduplicating {len(all_events)} total events")
    deduplicated_events = deduplicate_events(all_events)
    
    return {
        "events": deduplicated_events,
        "stats": {
            "cities_processed": len(CITIES),
            "events_scraped": len(all_events),
            "events_deduplicated": len(deduplicated_events),
            "cities": CITIES
        }
    } 