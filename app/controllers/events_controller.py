import logging
from flask import jsonify, request

def search_events(meili_client):
    """Search events endpoint."""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('q') if data else None
    else:  # GET
        query = request.args.get("q")

    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        index = meili_client.index("events")
        results = index.search(query)
        return jsonify(results), 200
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return jsonify({"error": str(e)}), 500

def refresh_events(meili_client):
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
        success = save_events_to_meilisearch(events, meili_client)
        
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