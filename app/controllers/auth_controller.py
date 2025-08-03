import jwt
import random
from datetime import datetime, timedelta
from flask import jsonify, request
from twilio.rest import Client

class AuthController:
    def __init__(self, app, users):
        self.app = app
        self.users = users
        self.logger = app.logger
        self.twilio_client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

    def _generate_otp(self):
        return str(random.randint(100000, 999999))

    def send_otp(self):
        self.logger.info("Received request for OTP")
        data = request.get_json()
        phone_number = data.get('phoneNumber')

        if not phone_number:
            self.logger.warning("OTP request failed: Phone number missing")
            return jsonify({"error": "Phone number is required"}), 400

        self.logger.info(f"Processing OTP request for phone number: {phone_number}")

        user = next((u for u in self.users.values() if u['phoneNumber'] == phone_number), None)

        # For this example, we'll create a new user if they don't exist.
        if not user:
            self.logger.info(f"Phone number not found. Creating new user for: {phone_number}")
            new_user_id = str(len(self.users) + 1)
            user = {
                "phoneNumber": phone_number,
                "name": f"User {new_user_id}",
                "otp": None,
                "otp_expiration": None
            }
            self.users[new_user_id] = user
        else:
            self.logger.info(f"Found existing user for phone number: {phone_number}")

        otp = self._generate_otp()
        user['otp'] = otp
        user['otp_expiration'] = datetime.utcnow() + timedelta(minutes=10)
        self.logger.info(f"Generated OTP {otp} for {phone_number}")

        # In a real app, you would uncomment this to send the SMS.
        # try:
        #     self.logger.info(f"Attempting to send OTP via Twilio to {phone_number}")
        #     message = self.twilio_client.messages.create(
        #         to=phone_number,
        #         from_=self.app.config['TWILIO_PHONE_NUMBER'],
        #         body=f"Your login code is: {otp}"
        #     )
        #     self.logger.info(f"Successfully sent OTP to {phone_number}. Message SID: {message.sid}")
        # except Exception as e:
        #     self.logger.error(f"Twilio failed to send OTP to {phone_number}: {e}")
        #     return jsonify({"error": "Failed to send OTP."}), 500
        
        # For demonstration, we'll print the OTP to the console.
        self.logger.info(f"DEMO MODE: OTP for {phone_number} is: {otp}")

        self.logger.info(f"Successfully processed OTP request for {phone_number}")
        return jsonify({"message": "An OTP has been sent to your phone number."})

    def verify_otp(self):
        self.logger.info("Received request to verify OTP")
        data = request.get_json()
        phone_number = data.get('phoneNumber')
        otp_received = data.get('otp')

        if not phone_number or not otp_received:
            self.logger.warning("OTP verification failed: Phone number or OTP missing from request")
            return jsonify({"error": "Phone number and OTP are required"}), 400

        self.logger.info(f"Processing OTP verification for {phone_number} with received OTP {otp_received}")

        user_id, user_data = next(
            ((uid, udata) for uid, udata in self.users.items() if udata['phoneNumber'] == phone_number),
            (None, None)
        )

        if not user_data:
            self.logger.warning(f"OTP verification failed for {phone_number}: User not found")
            return jsonify({"error": "Invalid or expired OTP."}), 401

        if user_data.get('otp') != otp_received:
            self.logger.warning(f"OTP verification failed for {phone_number}: Received OTP {otp_received} does not match stored OTP {user_data.get('otp')}")
            return jsonify({"error": "Invalid or expired OTP."}), 401

        if datetime.utcnow() > user_data.get('otp_expiration', datetime.min):
            self.logger.warning(f"OTP verification failed for {phone_number}: OTP has expired.")
            return jsonify({"error": "Invalid or expired OTP."}), 401

        self.logger.info(f"OTP successfully verified for {phone_number}")

        # Clear the OTP after successful verification
        user_data['otp'] = None
        user_data['otp_expiration'] = None

        self.logger.info(f"Generating JWT for user ID {user_id}")
        token = jwt.encode({
            'userId': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, self.app.config['SECRET_KEY'], algorithm="HS256")
        
        user_profile = {
            'userId': user_id,
            'name': user_data.get('name'),
            'phoneNumber': user_data.get('phoneNumber')
        }

        self.logger.info(f"Successfully completed login for user ID {user_id}")
        return jsonify({'token': token, 'user': user_profile})

def initialize_auth_controller(app, users):
    return AuthController(app, users) 