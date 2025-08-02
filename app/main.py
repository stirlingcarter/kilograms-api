import os
import sys
import meilisearch
import logging
from flask import Flask, jsonify, request

# Add the current directory to Python path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

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

@app.route("/events/refresh", methods=['POST'])
def refresh_events():
    """Refresh events by scraping all cities and saving to Meilisearch."""
    try:
        # Import the orchestrator (with error handling)
        try:
            from src.orchestrator import refresh_all_events
            from src.meilisearch_client import save_events_to_meilisearch
        except ImportError as e:
            return jsonify({"error": f"Missing required modules: {str(e)}"}), 500
        
        # Get all events and stats
        result = refresh_all_events()
        events = result["events"]
        stats = result["stats"]
        
        # Save to Meilisearch
        success = save_events_to_meilisearch(events, client)
        
        if not success:
            return jsonify({
                "error": "Failed to save to Meilisearch",
                **stats
            }), 500
        
        return jsonify({
            "status": "success",
            **stats
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