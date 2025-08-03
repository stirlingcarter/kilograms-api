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

# Import controllers and services
from controllers.home_controller import get_home
from controllers.events_controller import events_controller
from controllers.users_controller import initialize_users_controller
from controllers.auth_controller import initialize_auth_controller
from services.user_service import initialize_user_service


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-and-long-string'

# Twilio Configuration
app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID')
app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN')
app.config['TWILIO_PHONE_NUMBER'] = os.environ.get('TWILIO_PHONE_NUMBER')

# Initialize services
user_service = initialize_user_service(app)

# Initialize controllers
# Note: users_controller may need to be updated to use user_service as well,
# but for now we leave it as is to focus on the auth flow.
users_controller = initialize_users_controller(app, {}) # Passing empty dict as in-memory store is no longer used
auth_controller = initialize_auth_controller(app, user_service)

# Attach user_service to the app context so decorators can access it
app.user_service = user_service

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

@app.route('/auth/otp/send', methods=['POST'])
def send_otp():
    return auth_controller.send_otp()

@app.route('/auth/otp/verify', methods=['POST'])
def verify_otp():
    return auth_controller.verify_otp()

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

@app.route('/test-logging')
def test_logging():
    app.logger.info("This is an INFO test log message.")
    app.logger.warning("This is a WARNING test log message.")
    app.logger.error("This is an ERROR test log message.")
    return "Log messages sent! Check CloudWatch.", 200 