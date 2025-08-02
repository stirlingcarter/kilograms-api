import os
import meilisearch
from flask import Flask, jsonify, request

app = Flask(__name__)

# Meilisearch client setup
MEILI_URL = "http://18.217.93.15:7700"
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

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    try:
        index = client.index("events")
        results = index.search(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 