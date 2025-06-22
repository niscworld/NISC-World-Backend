from flask import Blueprint, jsonify, request
from app.models import User, Profile, Interns, InternshipApply, Internships, db
from app.utils import generate_string, generate_username, send_email_to, get_current_time
from werkzeug.security import generate_password_hash
from config import GeneralSettings


api = Blueprint("internship_api", __name__)

@api.route('/get-internships', methods=['GET'])
def get_internships():
    try:
        internships = Internships.query.filter_by(is_visible=True).order_by(Internships.posted_on.desc()).all()

        result = []
        for i in internships:
            result.append({
                'id': i.id,
                'code': i.code,
                'title': i.title,
                'description': i.description,
                'department': i.department,
                'duration': i.duration,
                'location': i.location,
                'stipend': i.stipend,
                'posted_on': i.posted_on.strftime('%Y-%m-%d') if i.posted_on else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching internships: {str(e)}'}), 500





@api.route('/apply-internship', methods=['POST'])
def apply_internship():
    data = request.get_json()
    print(data)

    fullname = data.get('fullname')
    email = data.get('email')
    resume_url = data.get('resume_url')
    internship_code = data.get('internship_code')

    if not fullname or not internship_code:
        return jsonify({'message': 'Full name and internship code are required.'}), 400

    # ✅ Check if already applied using email + internship_code
    existing_application = InternshipApply.query.filter_by(
        email=email,
        internship_code=internship_code
    ).first()

    if existing_application:
        return jsonify({'message': 'You have already applied for this internship.'}), 409

    # ✅ Check internship existence and if applications are open
    internship = Internships.query.filter_by(code=internship_code).first()
    if not internship:
        return jsonify({'message': 'Internship not found.'}), 404

    if not internship.can_join:
        return jsonify({'message': 'Applications for this internship are currently closed.'}), 403

    # ✅ Save the application
    try:
        application = InternshipApply(
            fullname=fullname,
            email=email,
            resume_url=resume_url,
            internship_code=internship_code
        )

        db.session.add(application)
        db.session.commit()

        return jsonify({'message': 'Application submitted successfully.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500




@api.route('/accept-internship', methods=['POST'])
def accept_internship():
    data = request.get_json()
    email = data.get('email')
    internship_code = data.get('internship_code')
    message_from_hr = data.get('message', '').strip()  # ✅ Optional custom message

    if not email or not internship_code:
        return jsonify({'message': 'Missing email or internship_code'}), 400

    # ✅ Step 1: Check application exists
    application = InternshipApply.query.filter_by(email=email, internship_code=internship_code).first()
    if not application:
        return jsonify({'message': 'Application not found'}), 404

    # ✅ Step 2: Check internship exists
    internship = Internships.query.filter_by(code=internship_code).first()
    if not internship:
        return jsonify({'message': 'Internship not found'}), 404

    # ✅ Step 3: Generate username and password
    username = generate_username('intern')
    raw_password = generate_string()
    password_hash = generate_password_hash(raw_password)

    # ✅ Step 4: Create User
    new_user = User(user_id=username, password_hash=password_hash, is_active=True)
    db.session.add(new_user)

    # ✅ Step 5: Create Profile
    profile = Profile(user_id=username, fullname=application.fullname, email=email, position='Intern')
    db.session.add(profile)

    # ✅ Step 6: Add to Interns Table
    intern = Interns(user_id=username, internship_code=internship_code, completion_status='ongoing')
    db.session.add(intern)

    # ✅ Step 7: Remove or mark application (optional - here marking complete)
    db.session.delete(application)

    # ✅ Step 8: Commit changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error saving data: {str(e)}'}), 500

    # ✅ Step 9: Send email with credentials + custom message
    subject = "🎉 Internship Accepted - Login Credentials - NISC World"
    
    body = f"""
Hi {application.fullname},

Congratulations! Your internship application for ({internship.title}) has been accepted.

Here are your login credentials:

🔐 Username: {username}
🔑 Password: {raw_password}
Login here: https://www.nisc.co.in

"""

    if message_from_hr:
        body += f"📩 Message from HR:\n{message_from_hr}\n\n"

    body += f"""Please login and begin your journey.

Best wishes,  
HR Team

{GeneralSettings.MAIL_END_NOTE}
"""

    send_status = send_email_to(application.fullname, email, subject, body)

    return jsonify({
        'message': '✅ Applicant accepted and user created',
        'username': username,
        'email_sent': send_status
    }), 200
