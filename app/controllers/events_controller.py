import os
import logging
import meilisearch
from flask import jsonify, request

class EventsController:
    """Controller for events-related endpoints with Meilisearch integration."""
    
    def __init__(self):
        # Meilisearch client setup
        self.meili_url = os.getenv("MEILI_URL", "http://18.217.93.15:7700")
        self.meili_api_key = os.getenv("MEILI_API_KEY")
        self.client = meilisearch.Client(self.meili_url, self.meili_api_key)
    
    def health(self):
        """Health check endpoint for Meilisearch."""
        try:
            health = self.client.health()
            return jsonify({"status": "ok", "meilisearch": health}), 200
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return jsonify({"status": "error", "meilisearch": str(e)}), 503
    
    def search(self):
        """Search events endpoint."""
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('q') if data else None
        else:  # GET
            query = request.args.get("q")

        if not query:
            return jsonify({"error": "Missing query parameter 'q'"}), 400

        try:
            index = self.client.index("events")
            results = index.search(query)
            return jsonify(results), 200
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return jsonify({"error": str(e)}), 500

    def refresh(self):
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
            success = save_events_to_meilisearch(events, self.client)
            
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

# Create a global instance to use in routes
events_controller = EventsController() 