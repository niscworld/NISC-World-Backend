
from flask import Blueprint, jsonify, request, session
import jwt
from config import Config, GeneralSettings
from app.utils import find_user_by_id, create_session, get_add_delta_to_current_time_for_session, generate_string, get_user_profile, verify_dashboard_access, delete_session

api = Blueprint("api", __name__)

@api.route('/sign-in-as', methods=["POST", "GET"])
@verify_dashboard_access
def signInAs():
    data = request.get_json()
    owner_id = data.get('user_id')
    jwt_token = data.get('token')
    sign_in_as = data.get('sign_in_as')
    user = find_user_by_id(sign_in_as)
    if not user:
        return jsonify({"message": "User not found"}), 401

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

    profile = get_user_profile(user.user_id)

    # ✅ Track session
    create_session(
        user_id=user.user_id,
        jwt_token=token,
        refresh_token=refresh_token,
        ip_address=ip,
        user_agent=ua,
        expires_at=payload["exp"]
    )

    delete_session(user_id=owner_id, jwt_token=jwt_token)

    # ✅ Return response
    return jsonify({
        "message": "Login successful",
        "token": token,
        "refresh_token": refresh_token,
        "user": user.user_id,
        "fullname": profile.fullname,
        "email": profile.email,
        "position": profile.position,
        "expires_at": expiry_datetime.isoformat()  # 💡 Frontend can parse this ISO string
    }), 200

