# app/utils.py
from app import db
from app.models import User, Session
from app.util_functions import get_current_time  # to avoid circular import

def find_user_by_id(user_id):
    return User.query.filter_by(user_id=user_id).first()

def create_session(user_id, jwt_token, refresh_token=None, ip_address=None, user_agent=None, expires_at=None):
    session = Session(
        user_id=user_id,
        jwt_token=jwt_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=get_current_time(),
        expires_at=expires_at,
        revoked=False
    )
    db.session.add(session)
    db.session.commit()
    return session

def revoke_user_sessions(user_id):
    sessions = Session.query.filter_by(user_id=user_id, revoked=False).all()
    for session in sessions:
        session.revoked = True
    db.session.commit()

def verify_password(user_obj, password):
    return user_obj.check_password(password)
