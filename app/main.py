import os
import meilisearch
from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor

from app.src.scrapers.nineteen_hz import get_19hz_events
from app.src.normalizer import normalize_ra_event
from app.src.deduplicator import deduplicate_events
from app.src.savers import save_to_meilisearch

app = Flask(__name__)

# Meilisearch client setup
MEILI_URL = os.getenv("MEILI_URL", "http://18.217.93.15:7700")
MEILI_API_KEY = os.getenv("MEILI_API_KEY")

client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)

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
    Refreshes the events data by scraping from 19hz.info for all regions,
    normalizing, deduplicating, and saving to Meilisearch.
    """
    region_urls = {
        "sf": "https://19hz.info/eventlisting_BayArea.php",
        "la": "https://19hz.info/eventlisting_LosAngeles.php",
        "seattle": "https://19hz.info/eventlisting_Seattle.php",
        "atlanta": "https://19hz.info/eventlisting_Atlanta.php",
        "miami": "https://19hz.info/eventlisting_Miami.php",
        "dc": "https://19hz.info/eventlisting_DC.php",
        "chicago": "https://19hz.info/eventlisting_Chicago.php",
        "detroit": "https://19hz.info/eventlisting_Detroit.php",
        "denver": "https://19hz.info/eventlisting_Denver.php",
        "vegas": "https://19hz.info/eventlisting_LasVegas.php",
        "portland": "https://19hz.info/eventlisting_Portland.php"
    }
    regions = list(region_urls.keys())
    
    all_events = []
    with ThreadPoolExecutor() as executor:
        # Scrape events for all regions in parallel
        future_to_region = {executor.submit(get_19hz_events, region): region for region in regions}
        for future in future_to_region:
            region = future_to_region[future]
            try:
                events = future.result()
                all_events.extend(events)
            except Exception as exc:
                print(f'{region} generated an exception: {exc}')

    # Normalize, deduplicate, and save
    normalized_events = [normalize_ra_event(e) for e in all_events if e]
    deduplicated_events = deduplicate_events([e for e in normalized_events if e])
    save_to_meilisearch(deduplicated_events)
    
    return jsonify({
        "status": "ok",
        "message": f"Refreshed and saved {len(deduplicated_events)} events to Meilisearch."
    }), 200 