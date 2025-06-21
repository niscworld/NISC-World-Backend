# app/accounts/api.py

from flask import Blueprint, jsonify, request
from app.models import User
import jwt
from datetime import timedelta
from config import Config
from app.utils import find_user_by_id, verify_password, create_session, get_current_time, get_add_delta_to_current_time_for_session, generate_string

api = Blueprint("accounts_api", __name__)

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"message": "Missing credentials"}), 400

    user = find_user_by_id(user_id)
    if not user: 
        return jsonify({"message": "User not found"}), 401

    if not verify_password(user, password):
        return jsonify({"message": "Invalid ID or password"}), 401

    # Create JWT (you can customize payload as needed)
    payload = {
        "user_id": user.user_id,
        "exp": get_add_delta_to_current_time_for_session()
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    # Optional: Create a refresh token if you plan to use it
    refresh_token = generate_string()  # Add logic if needed

    # Track session
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')

    create_session(
        user_id=user.user_id,
        jwt_token=token,
        refresh_token=refresh_token,
        ip_address=ip,
        user_agent=ua,
        expires_at=payload["exp"]
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.user_id
    }), 200
