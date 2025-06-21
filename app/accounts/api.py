# api.py (or wherever your Flask Blueprint lives)
from flask import Blueprint, jsonify, request
from config import Config

api = Blueprint("api", __name__)

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user_id = data.get('id')
    password = data.get('password')

    # Dummy check — replace with your real DB/auth logic
    if user_id == "admin" and password == "password123":
        return jsonify({
            "message": "Login successful",
            "user": user_id,
            # "token": "your_generated_token_here"
        }), 200
    else:
        return jsonify({
            "message": "Invalid ID or Password"
        }), 401
