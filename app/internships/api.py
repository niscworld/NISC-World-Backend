from flask import Blueprint, jsonify, request
from app.models import User, Profile, Interns, InternshipApply, Internships, db
from app.utils import generate_string, generate_username, send_email_to, get_current_time, verify_dashboard_access, create_internship
from werkzeug.security import generate_password_hash
from config import GeneralSettings


api = Blueprint("internship_api", __name__)

@api.route('/get-internships', methods=['GET', 'POST'])
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
                'can_join': i.can_join,
                'is_visible': i.is_visible,
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

        # ✅ Send Thank You Email
        subject = "✅ Thank You for Applying - Internship at NISC World"

        body = f"""
Hi {fullname},

Thank you for applying for the internship opportunity: **{internship.title}** at NISC World.

We have received your application and our team will review it shortly.  
If selected, you will be contacted via this email address ({email}) with the next steps.

You can always reach out to us if you have any questions.

Best regards,  
HR Team  
NISC World

{GeneralSettings.MAIL_END_NOTE}
"""

        send_status = send_email_to(fullname, email, subject, body)

        return jsonify({
            'message': 'Application submitted successfully.',
            'email_sent': send_status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500





@api.route('/accept-internship', methods=['POST'])
def accept_internship():
    print("Accepting...1")
    data = request.get_json()
    email = data.get('email')
    internship_code = data.get('internship_code')
    message_from_hr = data.get('message', '').strip()  # ✅ Optional custom message

    print("Accepting...2")
    if not email or not internship_code:
        return jsonify({'message': 'Missing email or internship_code'}), 400

    # ✅ Step 1: Check application exists
    application = InternshipApply.query.filter_by(email=email, internship_code=internship_code).first()
    if not application:
        return jsonify({'message': 'Application not found'}), 404

    print("Accepting...3")
    # ✅ Step 2: Check internship exists
    internship = Internships.query.filter_by(code=internship_code).first()
    if not internship:
        return jsonify({'message': 'Internship not found'}), 404

    print("Accepting...4")
    # ✅ Step 3: Generate username and password
    username = generate_username('intern')
    raw_password = generate_string()
    password_hash = generate_password_hash(raw_password)

    print("Accepting...5")
    # ✅ Step 4: Create User
    new_user = User(user_id=username, password_hash=password_hash, is_active=True)
    db.session.add(new_user)

    print("Accepting...6")
    # ✅ Step 5: Create Profile
    profile = Profile(user_id=username, fullname=application.fullname, email=email, position='Intern')
    db.session.add(profile)

    print("Accepting...7")
    # ✅ Step 6: Add to Interns Table
    intern = Interns(user_id=username, internship_code=internship_code, completion_status='ongoing')
    db.session.add(intern)

    print("Accepting...8")
    # ✅ Step 7: Remove or mark application (optional - here marking complete)
    db.session.delete(application)

    print("Accepting...9")
    # ✅ Step 8: Commit changes
    try:
        print("Accepting...10")
        db.session.commit()
    except Exception as e:
        print("Accepting...11")
        print(e)
        db.session.rollback()
        return jsonify({'message': f'Error saving data: {str(e)}'}), 500
    print("Accepting...12")

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

    print("Accepting...13")
    send_status = send_email_to(application.fullname, email, subject, body)

    print("Accepting...14")
    return jsonify({
        'message': '✅ Applicant accepted and user created',
        'username': username,
        'email_sent': send_status
    }), 200


@api.route('/reject-internship', methods=['POST'])
def reject_internship():
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

    # ✅ Step 3: Delete or mark application as rejected
    db.session.delete(application)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating data: {str(e)}'}), 500

    # ✅ Step 4: Send rejection email
    subject = "📩 Internship Application Update - NISC World"

    body = f"""
Hi {application.fullname},

Thank you for applying for the internship position: **{internship.title}**.

We appreciate the time and effort you put into your application. After careful consideration, we regret to inform you that your application has not been selected for this internship round.
"""

    if message_from_hr:
        body += f"\n📩 Message from HR:\n{message_from_hr}\n"

    body += f"""

We encourage you to apply for future opportunities with us.

Best regards,  
HR Team

{GeneralSettings.MAIL_END_NOTE}
"""

    send_status = send_email_to(application.fullname, email, subject, body)

    return jsonify({
        'message': '❌ Applicant rejected and application removed',
        'email_sent': send_status
    }), 200




@api.route('/view-interns', methods=['GET', 'POST'])
@verify_dashboard_access
def view_interns():
    internship_code = None

    if request.method == 'POST':
        data = request.get_json()
        internship_code = data.get('internship_code')

    query = (
        db.session.query(Interns, Profile, Internships)
        .join(Profile, Profile.user_id == Interns.user_id)
        .join(Internships, Internships.code == Interns.internship_code)
    )

    if internship_code:
        query = query.filter(Interns.internship_code == internship_code)

    interns = query.all()

    result = []
    for intern, profile, internship in interns:
        result.append({
            'user_id': intern.user_id,
            'fullname': profile.fullname,
            'email': profile.email,
            'internship_title': internship.title,
            'internship_code': internship.code,
            'completion_status': intern.completion_status,
        })

    return jsonify(result), 200


@api.route('/send-message-to-intern', methods=['POST'])
def send_message_to_intern():
    data = request.get_json()
    email = data.get('email')
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    if not email or not subject or not body:
        return jsonify({'message': 'Missing email, subject, or body'}), 400

    send_status = send_email_to("Intern", email, subject, body)

    return jsonify({'message': '📩 Message sent', 'email_sent': send_status}), 200





@api.route('/view-my-internship', methods=['POST'])
def view_my_internship():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'success': False, 'message': 'User ID missing'}), 400

    internship_record = (
        db.session.query(Interns)
        .filter_by(user_id=user_id)
        .join(Internships)
        .first()
    )

    if not internship_record:
        return jsonify({'success': False, 'message': 'No internship found'}), 404

    internship = internship_record.internship
    hr_profile = internship.hr

    return jsonify({
        'success': True,
        'data': {
            'title': internship.title,
            'description': internship.description,
            'duration': internship.duration,
            'department': internship.department,
            'stipend': internship.stipend,
            'completion_status': internship_record.completion_status,
            'hr_name': hr_profile.fullname if hr_profile else 'N/A'
        }
    })

@api.route('/create-internships', methods=['POST'])
@verify_dashboard_access
def createInternship():
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    department = data.get('department')
    duration = data.get('duration')
    location = data.get('location')
    stipend = data.get('stipend')

    if not title:
        return jsonify({'message': 'Title is required'}), 400
    return create_internship(title=title, description=description, department=department, duration=duration, location=location, stipend=stipend)



@api.route('/get-internships-details', methods=['POST'])
def get_internships_details():
    try:
        internships = Internships.query.order_by(Internships.posted_on.desc()).all()

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
                'can_join': i.can_join,
                'is_visible': i.is_visible,
                'posted_on': i.posted_on.strftime('%Y-%m-%d') if i.posted_on else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'message': f'Error fetching internships: {str(e)}'}), 500



@api.route('/update-internships', methods=['PUT'])
@verify_dashboard_access
def update_internship():
    data = request.get_json()

    internship_code = data.get('code')
    if not internship_code:
        return jsonify({'message': 'Internship ID is required.'}), 400

    try:
        internship = Internships.query.filter_by(code=internship_code).first()
        if not internship:
            return jsonify({'message': 'Internship not found.'}), 404

        # ✅ Update only provided fields
        internship.title = data.get('title', internship.title)
        internship.description = data.get('description', internship.description)
        internship.department = data.get('department', internship.department)
        internship.duration = data.get('duration', internship.duration)
        internship.location = data.get('location', internship.location)
        internship.stipend = data.get('stipend', internship.stipend)
        internship.is_visible = data.get('is_visible', internship.is_visible)
        internship.can_join = data.get('can_join', internship.can_join)

        db.session.commit()

        return jsonify({'message': 'Internship updated successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating internship: {str(e)}'}), 500
