from functools import wraps
from flask import session, redirect, url_for, flash, request
from config import Config, ThreadSettings
from app.util_functions import *
from app.util_mail import *
from app.util_models import *
from app.util_wraps import *
from app.util_mfa import *
import threading
from datetime import datetime, timedelta

# 🕒 Global timestamp to track last cleanup
last_cleanup_run_time = None
# 🕒 Global timestamp to track last MFA cleanup
last_mfa_cleanup_run_time = None

def whoami(user_id, role, token):
    # Check user's actual role
    if not token or not user_id or not role:
        return jsonify({'success': False, 'error': 'Missing token, user_id, or role'}), 400

    # Check for session
    session = Session.query.filter_by(user_id=user_id, jwt_token=token).first()

    if not session:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

    if session.expires_at and session.expires_at < get_current_time():
        return jsonify({'success': False, 'error': 'Token expired'}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if profile.position != role:
        return jsonify({'success': False, 'error': 'Role mismatch', 'correct_position': profile.position}), 403
    return jsonify({'success': True,})



# ✅ Frequent hook to call per-request
def frequentCallerFunction(app):
    print("Caller Functions [Triggered]")
    clean_expired_sessions_threaded(app)
    clean_expired_mfa_entries_threaded(app)


# ✅ Background cleanup runner using app context
def clean_expired_sessions_threaded(app):
    global last_cleanup_run_time
    now = get_current_time()
    min_interval = timedelta(minutes=ThreadSettings.NewSessionDeleteThread)

    if last_cleanup_run_time is None or now - last_cleanup_run_time > min_interval:
        print("[THREAD] Starting new session cleanup thread...")
        last_cleanup_run_time = now

        def cleanup_runner():
            with app.app_context():
                delete_expired_sessions()

        t = threading.Thread(target=cleanup_runner, name="SessionCleanupThread", daemon=True)
        t.start()
    else:
        print("[THREAD] Sessions Cleanup thread not started — last run was too recent.")

def clean_expired_mfa_entries_threaded(app):
    global last_mfa_cleanup_run_time
    now = get_current_time()
    min_interval = timedelta(minutes=ThreadSettings.MFACleanupThread)  # Add this to your config

    if last_mfa_cleanup_run_time is None or now - last_mfa_cleanup_run_time > min_interval:
        print("[THREAD] Starting new MFA cleanup thread...")
        last_mfa_cleanup_run_time = now

        def cleanup_runner():
            with app.app_context():
                delete_expired_mfa_entries()

        t = threading.Thread(target=cleanup_runner, name="MFACleanupThread", daemon=True)
        t.start()
    else:
        print("[THREAD] MFA Cleanup thread not started — last run was too recent.")
