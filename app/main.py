import os
import meilisearch
from flask import Flask, jsonify, request
import concurrent.futures
import logging
from src.scrapers.nineteen_hz import get_19hz_events
from src.normalizer import normalize_ra_event
from src.deduplicator import deduplicate_events
from src.savers import save_to_meilisearch

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Meilisearch client setup
MEILI_URL = os.getenv("MEILI_URL", "http://18.217.93.15:7700")
MEILI_API_KEY = os.getenv("MEILI_API_KEY")

client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)

# All available cities from 19hz
CITIES = ["sf", "la", "seattle", "atlanta", "miami", "dc", "chicago", "detroit", "denver", "vegas", "portland"]

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

@app.route("/events/refresh", methods=['POST'])
def refresh_events():
    """
    Fetches events from all cities in parallel and saves them to Meilisearch.
    Returns a summary of the operation.
    """
    try:
        logging.info("Starting event refresh for all cities")

        # Function to fetch and process events for a single city
        def fetch_city_events(city):
            try:
                logging.info(f"Fetching events for {city}")
                raw_events = get_19hz_events(city)

                # Normalize events
                normalized_events = []
                for event in raw_events:
                    # Add city info to the event data before normalizing
                    event['location'] = city
                    normalized_event = normalize_ra_event(event)
                    if normalized_event:
                        normalized_events.append(normalized_event)

                logging.info(f"Fetched {len(normalized_events)} events for {city}")
                return normalized_events
            except Exception as e:
                logging.error(f"Error fetching events for {city}: {e}")
                return []

        # Fetch events from all cities in parallel
        all_events = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_city = {executor.submit(fetch_city_events, city): city for city in CITIES}

            for future in concurrent.futures.as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    city_events = future.result()
                    all_events.extend(city_events)
                except Exception as e:
                    logging.error(f"Error processing {city}: {e}")

        # Deduplicate events
        logging.info(f"Deduplicating {len(all_events)} total events")
        deduplicated_events = deduplicate_events(all_events)

        # Save to Meilisearch
        logging.info(f"Saving {len(deduplicated_events)} deduplicated events to Meilisearch")

        # Use the existing client from main.py instead of creating a new one
        try:
            index = client.index("events")
            # Clear existing events first (optional - remove this line if you want to append)
            index.delete_all_documents()
            # Add new events
            index.add_documents(deduplicated_events, primary_key='id')

            return jsonify({
                "status": "success",
                "cities_processed": len(CITIES),
                "total_events_fetched": len(all_events),
                "deduplicated_events": len(deduplicated_events),
                "saved_to_meilisearch": True
            }), 200

        except Exception as e:
            logging.error(f"Failed to save events to MeiliSearch: {e}")
            return jsonify({
                "status": "partial_success",
                "cities_processed": len(CITIES),
                "total_events_fetched": len(all_events),
                "deduplicated_events": len(deduplicated_events),
                "saved_to_meilisearch": False,
                "error": str(e)
            }), 500

    except Exception as e:
        logging.error(f"Error in refresh_events: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500 