from functools import wraps
from flask import request, jsonify
from app.models import Session, Profile, db
from datetime import datetime
from app.util_functions import get_current_time

def verify_dashboard_access(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            token = data.get('token')
            user_id = data.get('user_id')
            role = data.get('role')

            print(f"{user_id} Checking For Role {role} from route {request.path}")

            if not token or not user_id or not role:
                return jsonify({'error': 'Missing token, user_id, or role'}), 400

            # Check for session
            session = Session.query.filter_by(user_id=user_id, jwt_token=token).first()

            if not session:
                return jsonify({'error': 'Invalid token'}), 401

            if session.expires_at and session.expires_at < get_current_time():
                return jsonify({'error': 'Token expired'}), 401

            # Check user's actual role
            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                return jsonify({'error': 'User not found'}), 404

            if profile.position != role:
                return jsonify({'error': 'Role mismatch', 'correct_position': profile.position}), 403

            return func(*args, **kwargs)
        return wrapper
