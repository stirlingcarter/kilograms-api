import logging
from flask import jsonify

def get_health(meili_client):
    """Health check endpoint."""
    try:
        health = meili_client.health()
        return jsonify({"status": "ok", "meilisearch": health}), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "meilisearch": str(e)}), 503 