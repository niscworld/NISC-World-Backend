# app/utils.py
from flask import jsonify
from app import db
import jwt
from app.models import User, Session, Profile, Internships, MFAVerification, CompletedInterns, CompletedInternships, InternshipApply, Interns, InternFinalAssignment
from config import Config, GeneralSettings
from app.util_functions import get_current_time, get_add_delta_to_current_time_for_session  # to avoid circular import
from app.util_mail import send_internship_completion_email

def find_user_by_id(user_id):
    print(f"Checking.. user presence... {user_id}")
    user = User.query.filter_by(user_id=user_id).first()
    return user

def get_user_profile(user_id):
    if not user_id:
        return None
    return Profile.query.filter_by(user_id=user_id).first()

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

def delete_expired_mfa_entries():
    """
    Deletes MFA verification records where `expires_at` has passed.
    """
    now = get_current_time()

    expired_mfa_records = MFAVerification.query.filter(
        MFAVerification.expires_at < now,
        MFAVerification.is_verified == True  # Optional: Only delete unverified
    ).all()

    print(f"🧹 Cleaning up {len(expired_mfa_records)} expired MFA record(s)...")

    for record in expired_mfa_records:
        print(record)
        db.session.delete(record)

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


def create_internship(title, description, department, duration, location, stipend):
    if not title:
        return jsonify({'message': 'Title is required'}), 400

    try:
        internship = Internships(
            title=title,
            description=description,
            department=department,
            duration=duration,
            location=location,
            stipend=stipend,
        )

        db.session.add(internship)
        db.session.commit()

        return jsonify({
            'message': 'Internship created successfully',
            'code': internship.code
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating internship: {str(e)}'}), 500

# This Function Will Close Internship by doing the following:
# All The Interns from interns table will be removed and will be added completedinterns table
# All The Applicants from internship_apply table will be removed
# Internship will be removed and added to completedinternships table
def close_internship(internship_code):
    internship = Internships.query.filter_by(code=internship_code).first()
    print(f"Closing internship: {internship_code}")
    if not internship:
        print(f"Internship not found: {internship_code}")
        return jsonify({'message': 'Internship not found'}), 404

    # Move internship to CompletedInternships
    print(f"Moving internship to completed internships: {internship_code}")
    completed_internship = CompletedInternships(
        internship_code=internship.code,
        title=internship.title,
        description=internship.description,
        department=internship.department,
        duration=internship.duration,
        location=internship.location,
        stipend=internship.stipend,
        posted_on=internship.posted_on,
        hr_profile_id=internship.hr_profile_id
    )
    db.session.add(completed_internship)
    db.session.flush()  # Flush to ensure internship is moved before next operations

    # Move all interns to CompletedInterns
    print(f"Moving interns for internship: {internship_code}")
    interns = Interns.query.filter_by(internship_code=internship_code).all()
    mails = []
    for intern in interns:
        # for each of the intern get the detiasil from User table and Profile Table
        user = User.query.filter_by(user_id=intern.user_id).first()
        profile = Profile.query.filter_by(user_id=intern.user_id).first()
        submission = InternFinalAssignment.query.filter_by(user_id=intern.user_id).first()
        print(f"Moving intern: {intern.user_id} for internship: {internship_code}")
        completed_intern = CompletedInterns(
            user_id=intern.user_id,
            internship_code=internship_code,
            completion_status="Completed",
            full_name=profile.fullname,  # Assuming full_name is available in Interns model
            excellence = submission.isExcellence if submission else False  # Assuming excellence is a boolean field
        )
        mails.append( (completed_intern.user_id, profile.email, completed_intern.full_name) )
        print(f"Adding completed intern: {completed_intern.user_id} for internship: {internship_code}")
        db.session.add(completed_intern)
        db.session.flush()  # Flush to ensure intern is removed before next iteration
        print(f"Deleting intern: {intern.user_id} for internship: {internship_code}")
        db.session.delete(intern)
        db.session.flush()  # Flush to ensure intern is removed before next iteration
        print(f"Deleting profile for user: {user.user_id} for internship: {internship_code}")
        db.session.delete(profile)
        db.session.flush()  # Flush to ensure intern is removed before next iteration
        sessions = Session.query.filter_by(user_id=user.user_id).all()
        for session in sessions:
            print(f"Deleting session for user: {user.user_id} for internship: {internship_code}")
            db.session.delete(session)
            db.session.flush()
        print(f"Deleting user: {user.user_id} for internship: {internship_code}")
        db.session.delete(user)
        db.session.flush()  # Flush to ensure intern is removed before next iteration
        print(f"Deleting submission for user: {intern.user_id} for internship: {internship_code}")
        db.session.delete(submission) if submission else None  # Delete submission if it exists
        db.session.flush()  # Flush to ensure intern is removed before next iteration
        print(f"Completed intern added: {completed_intern.user_id} for internship: {internship_code}")
    print(f"Removed {len(interns)} interns from internship: {internship_code}")

    # Remove all applicants
    print(f"Removing applicants for internship: {internship_code}")
    InternshipApply.query.filter_by(internship_code=internship_code).delete()
    print(f"Removed applicants for internship: {internship_code}")

    db.session.delete(internship)
    print(f"Removed internship: {internship_code}")

    db.session.commit()

    # Send mail to all the interns that the internship is closed
    # Details of the mail has to be: Internship Title, Internship Duration Only
    send_internship_completion_email(mails, internship.title, internship.duration)


    return jsonify({'message': 'Internship closed successfully'}), 200

# Create a function that will return the details of the completed intern it will take the intern id as parameter also with the internship that he completed
def get_completed_intern_details(intern_id):
    completed_intern = CompletedInterns.query.filter_by(user_id=intern_id).first()
    if not completed_intern:
        print(f"Completed intern not found: {intern_id}\n\n\n")
        return jsonify({'message': 'Intern not found'}), 404
    
    internship_code = completed_intern.internship_code
    if not internship_code:
        return jsonify({'message': 'Internship code not found for this intern'}), 404

    internship = CompletedInternships.query.filter_by(internship_code=internship_code).first()
    if not internship:
        return jsonify({'message': 'Internship not found'}), 404
    
    # hr details also add
    hr_profile = Profile.query.filter_by(user_id=internship.hr_profile_id).first() if internship.hr_profile_id else None
    hr_details = {
        'hr_profile_id': internship.hr_profile_id,
        'hr_name': hr_profile.fullname if hr_profile else "N/A",
        'hr_email': hr_profile.email if hr_profile else "N/A"
    }

    print(f"Returning details for completed intern: {completed_intern.user_id} for internship: {internship_code}")
    print("Is Excellence:", completed_intern.excellence)
    print("\n\n\n\n\n\n")

    return jsonify({
        'intern_id': completed_intern.id,
        'user_id': completed_intern.user_id,
        'full_name': completed_intern.full_name,
        'excellence': completed_intern.excellence,
        'internship_code': completed_intern.internship_code,
        'completion_status': completed_intern.completion_status,
        'internship_details': {
            'title': internship.title,
            'description': internship.description,
            'department': internship.department,
            'duration': internship.duration,
            'location': internship.location,
            'stipend': internship.stipend,
            'hr_details': hr_details,
            'posted_on': internship.posted_on if internship.posted_on else None
        }
    }), 200
