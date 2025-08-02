import os
import sys
import meilisearch
import logging
from flask import Flask

# Add the current directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import controllers
from controllers.home_controller import get_home
from controllers.health_controller import get_health
from controllers.events_controller import search_events, refresh_events

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Meilisearch client setup
MEILI_URL = os.getenv("MEILI_URL", "http://18.217.93.15:7700")
MEILI_API_KEY = os.getenv("MEILI_API_KEY")

client = meilisearch.Client(MEILI_URL, MEILI_API_KEY)

# Routes
@app.route("/")
def home():
    return get_home()

@app.route("/health")
def health():
    return get_health(client)

@app.route("/events/search", methods=['GET', 'POST'])
def events_search():
    return search_events(client)

@app.route("/events/refresh", methods=['POST'])
def events_refresh():
    return refresh_events(client) 