from flask import Blueprint, jsonify, request
from app.models import User, Profile, Interns, InternshipApply, Internships, db, AppMessages, InternFinalAssignment
from app.utils import generate_string, generate_username, send_email_to, get_current_time, verify_dashboard_access, create_internship, send_email_with_attachment
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from config import GeneralSettings
import tempfile
import os


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

    existing_email = Profile.query.filter_by(
        email=email
    ).all()

    if existing_email:
        for row in existing_email:
            uid = row.user_id
            intern = Interns.query.filter_by(user_id=uid, internship_code=internship_code).first()
            if intern:
                return jsonify({'message': 'You are already an intern in this Internship.'}), 409
            pass
        pass

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

@api.route('/view-interns-submissions', methods=['GET', 'POST'])
@verify_dashboard_access
def view_interns_submissions():
    internship_code = None

    if request.method == 'POST':
        data = request.get_json()
        internship_code = data.get('internship_code')

    query = (
        db.session.query(Interns, Profile, Internships, InternFinalAssignment)
        .join(Profile, Profile.user_id == Interns.user_id)
        .join(Internships, Internships.code == Interns.internship_code)
        .outerjoin(InternFinalAssignment, InternFinalAssignment.user_id == Interns.user_id)
    )

    if internship_code:
        query = query.filter(Interns.internship_code == internship_code)

    interns = query.all()

    result = []
    for intern, profile, internship, final_assignment in interns:
        if final_assignment and final_assignment.grade:
            continue
        result.append({
            'user_id': intern.user_id,
            'fullname': profile.fullname,
            'email': profile.email,
            'internship_title': internship.title,
            'internship_code': internship.code,
            'completion_status': intern.completion_status,
            'assignment_url': final_assignment.assignment_url if final_assignment else None,
            'submitted_on': final_assignment.submitted_on.isoformat() if final_assignment else None,
        })

    return jsonify(result), 200


@api.route('/send-mail-message-to-intern', methods=['POST'])
def send_mail_message_to_intern():
    data = request.get_json()
    email = data.get('email')
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    if not email or not subject or not body:
        return jsonify({'message': 'Missing email, subject, or body'}), 400

    send_status = send_email_to("Intern", email, subject, body)

    return jsonify({'message': '📩 Message sent', 'email_sent': send_status}), 200

@api.route('/send-message-to-intern', methods=['POST'])
def send_in_app_message_to_intern():
    data = request.get_json()

    receiver_id = data.get('user_id')  # the intern/user receiving the message
    sender_id = data.get('sender_id')  # HR or SYSTEM
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    # Validate required fields
    if not receiver_id or not subject or not body:
        return jsonify({'message': 'Missing user_id, subject, or body'}), 400

    # Create message instance
    message = AppMessages(
        sender_id=sender_id,           # nullable
        receiver_id=receiver_id,       # required (unless you build system-wide)
        subject=subject,
        body=body,
        sent_on=get_current_time()     # optional if default is defined
    )

    try:
        db.session.add(message)
        db.session.commit()
        return jsonify({'message': '🟢 In-app message sent', 'message_id': message.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '❌ Failed to send in-app message', 'error': str(e)}), 500





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
                'hr_profile_id': i.hr_profile_id,  # Added hr_profile_id
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

        # Update hr_profile_id (if provided)
        hr_profile_id = data.get('hr_profile_id')
        if hr_profile_id:
            internship.hr_profile_id = hr_profile_id

        db.session.commit()

        return jsonify({'message': 'Internship updated successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating internship: {str(e)}'}), 500





@api.route('/get-intern-messages', methods=['POST'])
def get_intern_messages():
    # Get intern_id from the request body
    data = request.get_json()
    intern_id = data.get('intern_id')

    if not intern_id:
        print("No Intern Id")
        return jsonify({'message': 'Intern ID is required.'}), 400

    # Fetch all messages for the given intern_id
    messages = AppMessages.query.filter_by(receiver_id=intern_id).all()

    # Convert messages to JSON format
    messages_data = []

    if not messages:
        return jsonify({'messages': messages_data}), 200

    for message in messages:
        messages_data.append({
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'subject': message.subject,
            'body': message.body,
            'sent_on': message.sent_on.isoformat()
        })

    return jsonify({'messages': messages_data}), 200





@api.route('/intern-submit-assignment', methods=['POST'])
def submit_assignment():
    data = request.get_json()

    user_id = data.get('user_id')
    action = data.get('action')  # Optional flag to distinguish check vs submit

    # TODO: Verify token, validate user, etc.

    # 1. If just checking submission status
    if action == 'check':
        existing = InternFinalAssignment.query.filter_by(user_id=user_id).first()
        return jsonify({
            'submitted': bool(existing),
            'url': existing.assignment_url if existing else '',
            'grade': existing.grade if existing and existing.grade else 0,
            'remarks': existing.message if existing and existing.message else 'No Remarks',
        }), 200

    url = data.get('url')
    # 2. Submit new assignment
    if not user_id or not url:
        return jsonify({'success': False, 'message': 'Missing user_id or url'}), 400

    existing = InternFinalAssignment.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Assignment already submitted'}), 409

    new_submission = InternFinalAssignment(
        user_id=user_id,
        assignment_url=url
    )

    db.session.add(new_submission)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Assignment submitted successfully'}), 200


@api.route('/accept-final-assignment', methods=["POST", "GET"])
def acceptFinalAssignment():
    data = request.get_json()
    intern_id = data.get('intern_id')
    internship_code = data.get('internship_code')
    isExcellence = data.get('isExcellence')
    grade = data.get('grade')
    message = data.get('message')
    intern = InternFinalAssignment.query.filter_by(user_id=intern_id).first()
    if not intern:
        return jsonify({'success': False, 'message': 'Assignment Not Found'}), 409
    intern.grade = int(grade)
    intern.message = message
    intern.isExcellence = isExcellence
    db.session.commit()
    return jsonify({'success': False, 'message': 'Assignment Graded'}), 200


@api.route('/reject-final-assignment', methods=["POST", "GET"])
def rejectFinalAssignment():
    data = request.get_json()
    intern_id = data.get('intern_id')
    internship_code = data.get('internship_code')
    message = data.get('message')
    print(intern_id)
    intern = InternFinalAssignment.query.filter_by(user_id=intern_id).first()
    if not intern:
        return jsonify({'success': False, 'message': 'Assignment Not Found'}), 409

    data = request.get_json()

    receiver_id = intern_id
    sender_id = data.get('user_id')  # HR or SYSTEM
    subject = "Internshpi Final Assignment Not Accepted"
    body = message

    # Validate required fields
    if not receiver_id or not subject or not body:
        return jsonify({'message': 'Missing user_id, subject, or body'}), 400

    # Create message instance
    message = AppMessages(
        sender_id=sender_id,           # nullable
        receiver_id=receiver_id,       # required (unless you build system-wide)
        subject=subject,
        body=body,
        sent_on=get_current_time()     # optional if default is defined
    )

    try:
        db.session.delete(intern)
        db.session.add(message)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '❌ Failed to send in-app message', 'error': str(e)}), 500
    return jsonify({'success': False, 'message': 'Assignment Rejected'}), 200






@api.route('/get-offer-letter-details/<string:intern_id>', methods=['GET'])
def get_offer_letter_details(intern_id):
    """Fetch intern details for offer letter generation"""
    # intern_id = request.args.get('intern_id')
    print("FETCHING OFFER LETTER DETAILS")
    if not intern_id:
        return jsonify({'error': 'Intern ID is required'}), 400

    try:
        # Get intern record
        intern = Interns.query.filter_by(user_id=intern_id).first()
        if not intern:
            return jsonify({'error': 'Intern not found'}), 404

        # Get intern profile
        print("FETCHING OFFER LETTER DETAILS")
        profile = Profile.query.filter_by(user_id=intern.user_id).first()
        print(profile)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        print("FETCHING OFFER LETTER DETAILS")
        # Get internship details
        internship = Internships.query.filter_by(code=intern.internship_code).first()
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        print(internship)

        # Get HR details
        hr_profile = Profile.query.filter_by(user_id=internship.hr_profile_id).first()
        if not hr_profile:
            return jsonify({'error': 'HR profile not found'}), 404

        response_data = {
            'intern_id': intern.id,
            'fullname': profile.fullname,
            'email': profile.email,
            'internship_title': internship.title,
            'stipend': internship.stipend,
            'location': internship.location,
            'duration': internship.duration,
            'hr_id': hr_profile.user_id,
            'hr_name': hr_profile.fullname
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error fetching offer letter details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/send-offer-letter', methods=['POST'])
def send_offer_letter():
    """Send offer letter via email"""
    if 'pdf_file' not in request.files or 'intern_id' not in request.form:
        print("Missing files or intern_id in request")  # Debug log
        print(f"Request files: {request.files}")  # Debug log
        print(f"Request form: {request.form}")  # Debug log
        return jsonify({'error': 'Missing required fields (pdf_file and intern_id)'}), 400

    try:
        intern_id = request.form['intern_id']
        pdf_file = request.files['pdf_file']

        # Debug logs
        print(f"Processing intern_id: {intern_id}")
        print(f"PDF file received: {pdf_file.filename}")

        # Get intern details
        intern = Interns.query.filter_by(user_id=intern_id).first()
        if not intern:
            print(f"Intern not found: {intern_id}")
            return jsonify({'error': 'Intern not found'}), 404

        profile = Profile.query.filter_by(user_id=intern.user_id).first()
        if not profile:
            print(f"Profile not found for user_id: {intern.user_id}")
            return jsonify({'error': 'Profile not found'}), 404

        # Create temp directory if not exists
        temp_dir = os.path.join(tempfile.gettempdir(), 'nisc_offer_letters')
        os.makedirs(temp_dir, exist_ok=True)

        # Save the PDF temporarily
        filename = secure_filename(f"offer_letter_{intern_id}.pdf")
        temp_path = os.path.join(temp_dir, filename)
        pdf_file.save(temp_path)
        print(f"PDF saved temporarily at: {temp_path}")

        # Email details
        subject = "NISC Internship Offer Letter"
        body = f"""Dear {profile.fullname},

Please find attached your internship offer letter from NISC.

Regards,
NISC HR Team
"""

        # Send email
        if not send_email_with_attachment(
            to_email=profile.email,
            subject=subject,
            body=body,
            attachment_path=temp_path,
            filename=filename
        ):
            raise Exception("Failed to send email")

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print("Temporary file removed")

        return jsonify({
            'message': 'Offer letter sent successfully',
            'to_email': profile.email,
            'intern_name': profile.fullname
        }), 200

    except Exception as e:
        print(f"Error in send_offer_letter: {str(e)}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': f'Failed to send offer letter: {str(e)}'}), 500