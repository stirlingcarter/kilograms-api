from flask import jsonify

def get_home():
    """Home page endpoint."""
    return "<h1>Kilograms API</h1><p>Welcome to the Kilograms Python API!</p>" 