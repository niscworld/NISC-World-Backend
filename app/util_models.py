# app/utils.py
from flask import jsonify
from app import db
import jwt
from app.models import User, Session
from config import Config, GeneralSettings
from app.util_functions import get_current_time, get_add_delta_to_current_time_for_session  # to avoid circular import

def find_user_by_id(user_id):
    print(f"Checking.. user presence... {user_id}")
    user = User.query.filter_by(user_id=user_id).first()
    return user

def create_session(user_id, jwt_token, refresh_token=None, ip_address=None, user_agent=None, expires_at=None):
    session = Session(
        user_id=user_id,
        jwt_token=jwt_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=get_current_time(),
        expires_at=expires_at,
    )
    db.session.add(session)
    db.session.commit()
    return session


def revoke_session(user_id, old_jwt, refresh_token):
    # ✅ Fetch session matching all details
    session = Session.query.filter_by(
        user_id=user_id,
        jwt_token=old_jwt,
        refresh_token=refresh_token,
    ).first()

    if not session:
        return jsonify({"message": "Session not found or already revoked"}), 401

    # ✅ Check if refresh token has expired
    if session.expires_at and session.expires_at < get_current_time():
        return jsonify({"message": "Refresh token expired"}), 401

    # ✅ Generate new JWT
    new_payload = {
        "user_id": user_id,
        "exp": get_add_delta_to_current_time_for_session(minutes=GeneralSettings.JWTExpireMinutes)
    }
    new_jwt = jwt.encode(new_payload, Config.SECRET_KEY, algorithm="HS256")

    # ✅ Update session with new token
    session.jwt_token = new_jwt
    session.expires_at = new_payload["exp"]
    db.session.commit()

    return jsonify({
        "message": "Token refreshed successfully",
        "token": new_jwt
    }), 200


def delete_expired_sessions():
    """
    Deletes sessions where `expires_at` is set and the time has passed.
    """
    now = get_current_time()

    # Get all sessions that have expired
    expired_sessions = Session.query.filter(
        Session.expires_at != None,
        Session.expires_at < now
    ).all()

    print(f"🧹 Cleaning up {len(expired_sessions)} expired session(s)...")

    for session in expired_sessions:
        print(session)
        db.session.delete(session)

    db.session.commit()

def delete_session(user_id, jwt_token):
    session = Session.query.filter(
        Session.user_id==user_id,
        Session.jwt_token==jwt_token
    ).first()
    db.session.delete(session)
    db.session.commit()
    pass

def verify_password(user_obj, password):
    return user_obj.check_password(password)

