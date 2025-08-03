from flask import jsonify, request

class UsersController:
    def __init__(self, app, users):
        self.app = app
        self.users = users

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