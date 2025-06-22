from flask import jsonify
from app.models import MFAVerification, db
from app.util_functions import generate_otp, get_add_delta_to_current_time_for_session, get_current_time
from datetime import datetime, timedelta
from config import GeneralSettings



def create_mfa_entry(user, verify_for, otp_length=6):
    """
    Creates an MFA entry for a given user and purpose.
    
    Params:
    - user: str (user_id or email)
    - verify_for: str (LOGIN, InternApply, etc.)
    - otp_length: int (default 6-digit OTP)

    Returns:
    - dict: {'success': True, 'otp': '123456'} or error message
    """
    try:
        otp = generate_otp(length=otp_length)
        expire_duration = GeneralSettings.MFA_OTP_EXPIRE_DURATION
        expiry_time = get_add_delta_to_current_time_for_session(minutes=expire_duration)

        # Optional: Clear old unverified OTPs for same user + purpose
        MFAVerification.query.filter_by(user=user, verify_for=verify_for, is_verified=False).delete()

        mfa = MFAVerification(
            user=user,
            key=otp,
            verify_for=verify_for,
            expires_at=expiry_time
        )
        db.session.add(mfa)
        db.session.commit()

        return {'success': True, 'otp': otp}

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}


def verify_mfa_otp(user, otp, verify_for):
    if not user or not otp or not verify_for:
        return jsonify({'message': 'Missing fields'}), 400

    record = MFAVerification.query.filter_by(user=user, key=otp, verify_for=verify_for, is_verified=False).first()

    if not record:
        return jsonify({'message': 'Invalid or Expired OTP'}), 400

    if record.expires_at < get_current_time():
        return jsonify({'message': 'OTP has expired'}), 400

    record.is_verified = True
    db.session.commit()

    return jsonify({'message': 'OTP verified successfully'}), 200
