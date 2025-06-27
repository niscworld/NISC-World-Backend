from flask import Blueprint, jsonify, request
from app.models import db, Internships, InternshipApply
from app.util_wraps import verify_dashboard_access

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
