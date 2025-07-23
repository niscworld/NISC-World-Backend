from flask import Blueprint, jsonify, request
from app.models import db, Internships, InternshipApply
from app.util_wraps import verify_dashboard_access
from app.utils import send_email_to, close_internship
from config import GeneralSettings

api = Blueprint("api", __name__)

@api.route('/get-internships', methods=['POST'])
@verify_dashboard_access
def view_applicants_grouped():
    try:
        # Query all internships
        internships = Internships.query.all()
        internship_list = []

        for internship in internships:
            internship_list.append({
                "code": internship.code,
                "title": internship.title,
                "duration": internship.duration,
                "location": internship.location,
                "department": internship.department if hasattr(internship, 'department') else "N/A"
            })

        return jsonify({"internships": internship_list}), 200

    except Exception as e:
        print(f"[ERROR] Failed to fetch internships: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@api.route('/view-applicants/<code>', methods=['POST'])
@verify_dashboard_access
def view_applicants(code):
    data = request.get_json()
    # verify credentials: data['user_id'], data['token'], data['role']
    apps = InternshipApply.query.filter_by(internship_code=code).all()
    out = []
    for a in apps:
        out.append({
            'fullname': a.fullname,
            'email': a.email,
            'resume_url': a.resume_url,
            'applied_on': a.applied_on.isoformat(),
            'internship_code': a.internship_code
        })
    print(out)
    return jsonify({'applicants': out}), 200

@api.route("/send-message-to-applicant", methods=['POST'])
@verify_dashboard_access
def send_message_to_applicant():
    data = request.get_json()
    email = data.get('email')
    internship_code = data.get('internship_code')
    message = data.get('message')
    applicant = InternshipApply.query.filter_by(internship_code=internship_code, email=email).first()
    internship = Internships.query.filter_by(code=internship_code).first()
    subject = "📩 Internship Application Update !!"
    body = f"""
Dear Applicant,

{message}

From
HR
NISC

{GeneralSettings.MAIL_END_NOTE}

"""
    send_status = send_email_to("Applicant", email, subject, body)
    return jsonify({
        'message': '❌ Applicant rejected and application removed',
        'email_sent': send_status
    }), 200


# Close the internship
@api.route('/close-internship', methods=['POST'])
@verify_dashboard_access
def closeInternship():
    data = request.get_json()
    internship_code = data.get('internship_code')

    if not internship_code:
        return jsonify({'message': 'Internship code is required'}), 400

    try:
        # Call the utility function to close the internship
        print(f"Closing internship with code: {internship_code}")
        response = close_internship(internship_code)
        return response

    except Exception as e:
        print(f"[ERROR] Failed to close internship: {e}")
        return jsonify({'message': f'Error closing internship: {str(e)}'}), 500