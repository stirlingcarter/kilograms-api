import jwt
from datetime import datetime, timedelta
from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

class UsersController:
    def __init__(self, app, users):
        self.app = app
        self.users = users

    def login(self):
        data = request.get_json()
        if not data or not data.get('phoneNumber') or not data.get('password'):
            return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

        phone_number = data.get('phoneNumber')
        password = data.get('password')

        user_id, user_data = next(
            ((uid, udata) for uid, udata in self.users.items() if udata['phoneNumber'] == phone_number),
            (None, None)
        )

        if not user_data or not check_password_hash(user_data['password'], password):
            return jsonify({'message': 'Invalid credentials!'}), 401

        token = jwt.encode({
            'userId': user_id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, self.app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token, 'userId': user_id})

    def get_my_profile(self, current_user, token_data):
        return jsonify({
            'userId': token_data['userId'],
            'name': current_user.get('name'),
            'phoneNumber': current_user.get('phoneNumber')
        })

    def get_user_profile(self, user_id):
        lookup_user = self.users.get(user_id)
        if not lookup_user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({
            'userId': user_id,
            'name': lookup_user.get('name')
        })

    def update_user_profile(self, user_id):
        update_data = request.get_json()
        user = self.users.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if 'name' in update_data:
            user['name'] = update_data['name']
        
        if 'phoneNumber' in update_data:
            user['phoneNumber'] = update_data['phoneNumber']

        return jsonify({'message': 'Profile updated successfully'}), 200

def initialize_users_controller(app, users):
    return UsersController(app, users) 