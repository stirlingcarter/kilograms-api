import os
import sys
import logging
import watchtower
import boto3
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
from app.auth.decorators import token_required, user_identity_required

# Add the current directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import controllers
from controllers.home_controller import get_home
from controllers.events_controller import events_controller
from controllers.users_controller import initialize_users_controller, users_controller


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-and-long-string'

# For this example, we'll use a simple in-memory dictionary as our user database.
# In a real application, you would connect to a database like PostgreSQL or MySQL.
# The password for the user is hashed for security.
users = {
    "1": {
        "phoneNumber": "1234567890",
        "password": generate_password_hash("password123", method='pbkdf2:sha256'),
        "name": "Test User"
    }
}

# Attach users to the app context so decorators can access it
app.users = users

# Initialize controllers
initialize_users_controller(app, users)

# Set up logging
if os.environ.get('FLASK_ENV') == 'production':
    boto3_client = boto3.client("logs", region_name="us-east-2")
    handler = watchtower.CloudWatchLogHandler(boto3_client=boto3_client, log_group_name=app.name)
    app.logger.addHandler(handler)
    logging.getLogger("werkzeug").addHandler(handler)
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

# Routes
@app.route("/")
def home():
    return get_home()

@app.route('/login', methods=['POST'])
def login():
    return users_controller.login()

@app.route('/users/me', methods=['GET'])
@token_required
def get_my_profile(current_user, token_data):
    return users_controller.get_my_profile(current_user, token_data)

@app.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user_profile(current_user, token_data, user_id):
    return users_controller.get_user_profile(user_id)

@app.route('/users/<user_id>', methods=['PUT'])
@token_required
@user_identity_required
def update_user_profile(current_user, token_data, user_id):
    return users_controller.update_user_profile(user_id)

@app.route("/events/health")
def events_health():
    return events_controller.health()

@app.route("/events/search", methods=['GET', 'POST'])
def events_search():
    return events_controller.search()

@app.route("/events/refresh", methods=['POST'])
def events_refresh():
    return events_controller.refresh() 