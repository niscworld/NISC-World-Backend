# app/accounts/api.py

from flask import Blueprint, jsonify, request
from app.models import User
import jwt
from datetime import timedelta
from config import Config, GeneralSettings
from app.utils import find_user_by_id, verify_password, create_session, get_current_time, get_add_delta_to_current_time_for_session, generate_string, revoke_session, delete_session

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

    # ✅ Create JWT with expiry
    expiry_datetime = get_add_delta_to_current_time_for_session(minutes=GeneralSettings.JWTExpireMinutes)
    payload = {
        "user_id": user.user_id,
        "exp": expiry_datetime,
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    # ✅ Generate refresh token
    refresh_token = generate_string()

    # ✅ Get client info
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')

    # ✅ Track session
    create_session(
        user_id=user.user_id,
        jwt_token=token,
        refresh_token=refresh_token,
        ip_address=ip,
        user_agent=ua,
        expires_at=payload["exp"]
    )

    # ✅ Return response
    return jsonify({
        "message": "Login successful",
        "token": token,
        "refresh_token": refresh_token,
        "user": user.user_id,
        "expires_at": expiry_datetime.isoformat()  # 💡 Frontend can parse this ISO string
    }), 200





@api.route('/refresh-token', methods=['POST'])
def refresh_token():
    data = request.get_json()
    user_id = data.get('user_id')
    old_jwt = data.get('jwt_token')
    refresh_token = data.get('refresh_token')

    if not user_id or not old_jwt or not refresh_token:
        return jsonify({"message": "Missing required fields"}), 400

    return revoke_session(user_id=user_id, old_jwt=old_jwt, refresh_token=refresh_token)



@api.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user_id = data.get('user_id')
    jwt_token = data.get('jwt_token')

    if not user_id or not jwt_token:
        return jsonify({"message": "Missing user_id or token"}), 400

    try:
        success = delete_session(user_id=user_id, jwt_token=jwt_token)
        if success:
            return jsonify({"message": "Logout successful"}), 200
        else:
            return jsonify({"message": "Session not found or already revoked"}), 404
    except Exception as e:
        print(f"[LOGOUT ERROR] {e}")
        return jsonify({"message": "Internal server error"}), 500
