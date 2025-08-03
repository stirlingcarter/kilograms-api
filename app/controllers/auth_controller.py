import jwt
import random
from datetime import datetime, timedelta
from flask import jsonify, request
from twilio.rest import Client

class AuthController:
    def __init__(self, app, users):
        self.app = app
        self.users = users
        self.twilio_client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])

    def _generate_otp(self):
        return str(random.randint(100000, 999999))

    def send_otp(self):
        data = request.get_json()
        phone_number = data.get('phoneNumber')

        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400

        user = next((u for u in self.users.values() if u['phoneNumber'] == phone_number), None)

        # For this example, we'll create a new user if they don't exist.
        if not user:
            new_user_id = str(len(self.users) + 1)
            user = {
                "phoneNumber": phone_number,
                "name": f"User {new_user_id}",
                "otp": None,
                "otp_expiration": None
            }
            self.users[new_user_id] = user

        otp = self._generate_otp()
        user['otp'] = otp
        user['otp_expiration'] = datetime.utcnow() + timedelta(minutes=10)

        # In a real app, you would uncomment this to send the SMS.
        # try:
        #     message = self.twilio_client.messages.create(
        #         to=phone_number,
        #         from_=self.app.config['TWILIO_PHONE_NUMBER'],
        #         body=f"Your login code is: {otp}"
        #     )
        #     print(f"OTP sent to {phone_number}: {message.sid}")
        # except Exception as e:
        #     print(f"Error sending OTP: {e}")
        #     return jsonify({"error": "Failed to send OTP."}), 500
        
        # For demonstration, we'll print the OTP to the console.
        print(f"OTP for {phone_number} is: {otp}")

        return jsonify({"message": "An OTP has been sent to your phone number."})

    def verify_otp(self):
        data = request.get_json()
        phone_number = data.get('phoneNumber')
        otp_received = data.get('otp')

        if not phone_number or not otp_received:
            return jsonify({"error": "Phone number and OTP are required"}), 400

        user_id, user_data = next(
            ((uid, udata) for uid, udata in self.users.items() if udata['phoneNumber'] == phone_number),
            (None, None)
        )

        if not user_data or user_data.get('otp') != otp_received:
            return jsonify({"error": "Invalid or expired OTP."}), 401

        if datetime.utcnow() > user_data.get('otp_expiration', datetime.min):
            return jsonify({"error": "Invalid or expired OTP."}), 401

        # Clear the OTP after successful verification
        user_data['otp'] = None
        user_data['otp_expiration'] = None

        token = jwt.encode({
            'userId': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, self.app.config['SECRET_KEY'], algorithm="HS256")
        
        user_profile = {
            'userId': user_id,
            'name': user_data.get('name'),
            'phoneNumber': user_data.get('phoneNumber')
        }

        return jsonify({'token': token, 'user': user_profile})

def initialize_auth_controller(app, users):
    return AuthController(app, users) 