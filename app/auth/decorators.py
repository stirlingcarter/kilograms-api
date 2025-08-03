import jwt
import logging
from functools import wraps
from flask import request, jsonify, current_app

def token_required(f):
    """
    Decorator to protect routes with JWT token authentication.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            secret_key = current_app.config['SECRET_KEY']
            user_service = current_app.user_service
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = data.get('userId')
            
            # Look up the user in DynamoDB to ensure they still exist
            current_user = user_service.find_user_by_id(user_id)
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            
        except Exception as e:
            logging.error(f"Token validation error: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, data, *args, **kwargs)
    return decorated

def user_identity_required(f):
    """
    Decorator to verify that the user from the token matches the user_id in the URL.
    """
    @wraps(f)
    def decorated(current_user, token_data, *args, **kwargs):
        route_user_id = kwargs.get('user_id')
        if not route_user_id or token_data.get('userId') != route_user_id:
            return jsonify({'message': 'Operation not permitted for this user.'}), 403
        return f(current_user, token_data, *args, **kwargs)
    return decorated 