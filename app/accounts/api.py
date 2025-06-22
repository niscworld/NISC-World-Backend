# app/accounts/api.py

from flask import Blueprint, jsonify, request, session
from app.models import User, Profile, db
import jwt
from datetime import timedelta
from config import Config, GeneralSettings
from app.utils import find_user_by_id, verify_password, create_session, get_current_time, get_add_delta_to_current_time_for_session, generate_string, revoke_session, delete_session, get_user_profile, create_mfa_entry, send_otp_email, verify_mfa_otp

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




@api.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    user = data.get('user')
    name = data.get('name', 'User')
    verify_for = data.get('verify_for')

    if not user or not verify_for:
        return jsonify({'message': 'Missing email or verification type'}), 400

    result = create_mfa_entry(user=user, verify_for=verify_for)

    if result.get('success'):
        otp = result['otp']
        if send_otp_email(name=name, to_email=user, otp=otp, purpose=verify_for):
            return jsonify({'message': 'OTP sent successfully'}), 200
        return jsonify({'message': 'Failed to send OTP email'}), 500
    return jsonify({'message': result.get('message', 'Failed to create OTP')}), 500

@api.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    user = data.get('user')
    otp = data.get('otp')
    verify_for = data.get('verify_for')

    return verify_mfa_otp(user, otp, verify_for)










@api.route('/view-profile', methods=['POST'])
def view_profile():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    return jsonify({
        'user_id': profile.user_id,
        'fullname': profile.fullname,
        'email': profile.email,
        'position': profile.position
    }), 200

@api.route('/edit-profile', methods=['PUT'])
def edit_profile():
    data = request.json
    profile = Profile.query.filter_by(user_id=data.get('user_id')).first()
    if profile:
        profile.fullname = data.get('fullname')
        profile.email = data.get('email')
        profile.position = data.get('position')
        db.session.commit()
        return jsonify({'message': 'Profile updated'})
    return jsonify({'message': 'Profile not found'}), 404


@api.route('/change-password', methods=['PUT'])
def change_password():
    data = request.json
    user_id = data.get('user_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.check_password(old_password):
        return jsonify({'message': 'Old password is incorrect'}), 401

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200