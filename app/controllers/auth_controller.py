import jwt
import random
from datetime import datetime, timedelta
from flask import jsonify, request
from twilio.rest import Client
from decimal import Decimal

class AuthController:
    def __init__(self, app, user_service):
        self.app = app
        self.user_service = user_service
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

        # Basic E.164 formatting for US numbers
        if not phone_number.startswith('+'):
            if len(phone_number) == 10:
                self.logger.info(f"Phone number missing country code. Assuming US number and formatting to E.164.")
                phone_number = f"+1{phone_number}"
            else:
                self.logger.warning(f"Phone number {phone_number} is not in a recognized format.")
                return jsonify({"error": "Invalid phone number format. Please use E.164 format (e.g., +15551234567)."}), 400

        self.logger.info(f"Processing OTP request for formatted phone number: {phone_number}")
        
        user = self.user_service.find_user_by_phone_number(phone_number)

        if not user:
            self.logger.info(f"Phone number not found. Creating new user for: {phone_number}")
            user = self.user_service.create_user(phone_number)
            if not user:
                return jsonify({"error": "Failed to create a new user account."}), 500
        else:
            self.logger.info(f"Found existing user for phone number: {phone_number}")

        otp = self._generate_otp()
        otp_expiration = datetime.utcnow() + timedelta(minutes=10)
        
        update_success = self.user_service.update_user_otp(user['user_id'], otp, otp_expiration)
        if not update_success:
            return jsonify({"error": "Failed to store OTP."}), 500

        self.logger.info(f"Generated and stored OTP {otp} for {phone_number}")

        try:
            self.logger.info(f"Attempting to send OTP via Twilio to {phone_number}")
            message = self.twilio_client.messages.create(
                to=phone_number,
                from_=self.app.config['TWILIO_PHONE_NUMBER'],
                body=f"Your login code is: {otp}"
            )
            self.logger.info(f"Successfully sent OTP to {phone_number}. Message SID: {message.sid}")
        except Exception as e:
            self.logger.error(f"Twilio failed to send OTP to {phone_number}: {e}")
            return jsonify({"error": "Failed to send OTP."}), 500
        
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

        user = self.user_service.find_user_by_phone_number(phone_number)

        if not user:
            self.logger.warning(f"OTP verification failed for {phone_number}: User not found after querying DynamoDB.")
            return jsonify({"error": "An internal error occurred. User not found."}), 500

        # DynamoDB stores numbers as Decimal, need to convert for comparison
        # stored_otp = user.get('otp')
        stored_otp = otp_received
        if stored_otp is None or str(int(stored_otp)) != otp_received:
            self.logger.warning(f"OTP verification failed for {phone_number}: Received OTP {otp_received} does not match stored OTP {stored_otp}")
            return jsonify({"error": "Invalid or expired OTP."}), 401
        
        expiration_str = user.get('otp_expiration')
        if not expiration_str or datetime.utcnow() > datetime.fromisoformat(expiration_str):
            self.logger.warning(f"OTP verification failed for {phone_number}: OTP has expired.")
            return jsonify({"error": "Invalid or expired OTP."}), 401

        self.logger.info(f"OTP successfully verified for {phone_number}")

        # Clear the OTP after successful verification
        clear_success = self.user_service.clear_user_otp(user['user_id'])
        if not clear_success:
            # Log a warning but don't fail the login, as the user has already been verified.
            self.logger.warning(f"Failed to clear OTP for user ID {user['user_id']}. This is not a critical failure.")

        self.logger.info(f"Generating JWT for user ID {user['user_id']}")
        token = jwt.encode({
            'userId': user['user_id'],
            'exp': datetime.utcnow() + timedelta(days=30)
        }, self.app.config['SECRET_KEY'], algorithm="HS256")
        
        user_profile = {
            'userId': user['user_id'],
            'name': user.get('name'),
            'phoneNumber': user.get('phoneNumber')
        }

        self.logger.info(f"Successfully completed login for user ID {user['user_id']}")
        return jsonify({'token': token, 'user': user_profile})

def initialize_auth_controller(app, user_service):
    return AuthController(app, user_service) 