import os
import sys
import logging
from flask import Flask

# Add the current directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import controllers
from controllers.home_controller import get_home
from controllers.events_controller import events_controller

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Routes
@app.route("/")
def home():
    return get_home()

@app.route("/events/health")
def events_health():
    return events_controller.health()

@app.route("/events/search", methods=['GET', 'POST'])
def events_search():
    return events_controller.search()

@app.route("/events/refresh", methods=['POST'])
def events_refresh():
    return events_controller.refresh() 