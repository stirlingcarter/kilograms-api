import os
import sys
import meilisearch
import logging
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request

# Add the current directory to Python path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.scrapers.nineteen_hz import get_19hz_events
    from src.normalizer import normalize_ra_event
    from src.deduplicator import deduplicate_events
    from src.schema import MusicEvent
except ImportError as e:
    logging.error(f"Failed to import src modules: {e}")
    # We'll handle this gracefully in the endpoint

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Meilisearch client setup
MEILI_URL = os.getenv("MEILI_URL", "http://18.217.93.15:7700")
MEILI_API_KEY = os.getenv("MEILI_API_KEY")

client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)

# Define all the cities we want to scrape
CITIES = ["sf", "la", "seattle", "atlanta", "miami", "dc", "chicago", "detroit", "denver", "vegas", "portland"]

def scrape_city_events(city: str) -> list:
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

@app.route("/")
def hello_world():
    return "<h1>Kilograms API</h1><p>Welcome to the Kilograms Python API!</p>"

@app.route("/health")
def health_check():
    try:
        health = client.health()
        return jsonify({"status": "ok", "meilisearch": health}), 200
    except Exception as e:
        return jsonify({"status": "error", "meilisearch": str(e)}), 503

@app.route("/events/refresh", methods=['POST'])
def refresh_events():
    """Refresh events by scraping all cities in parallel and saving to Meilisearch."""
    try:
        # Check if we have the required imports
        try:
            from src.scrapers.nineteen_hz import get_19hz_events
            from src.normalizer import normalize_ra_event
            from src.deduplicator import deduplicate_events
        except ImportError as e:
            return jsonify({"error": f"Missing required modules: {str(e)}"}), 500
            
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
        
        # Save to Meilisearch
        if deduplicated_events:
            logging.info(f"Saving {len(deduplicated_events)} deduplicated events to Meilisearch")
            try:
                index = client.index("events")
                index.add_documents(deduplicated_events, primary_key='id')
                logging.info("Successfully saved events to Meilisearch")
            except Exception as e:
                logging.error(f"Failed to save events to Meilisearch: {e}")
                return jsonify({
                    "error": f"Failed to save to Meilisearch: {str(e)}",
                    "events_scraped": len(all_events),
                    "events_deduplicated": len(deduplicated_events)
                }), 500
        
        return jsonify({
            "status": "success",
            "cities_processed": len(CITIES),
            "events_scraped": len(all_events),
            "events_deduplicated": len(deduplicated_events),
            "cities": CITIES
        }), 200
        
    except Exception as e:
        logging.error(f"Error in events refresh: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('q') if data else None
    else:  # GET
        query = request.args.get("q")

    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        index = client.index("events")
        results = index.search(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 