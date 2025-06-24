from flask import Blueprint, jsonify, request
from app.models import db, InternshipApply, Internships
from app.util_models import create_internship
from app.util_wraps import verify_dashboard_access

api = Blueprint("api", __name__)


@api.route('view-applicants', methods=['POST'])
@verify_dashboard_access
def view_applicants_grouped():
    try:
        applications = InternshipApply.query.order_by(InternshipApply.applied_on.desc()).all()

        # Build a dictionary to group by internship_code
        grouped_data = {}

        for app in applications:
            code = app.internship_code
            if code not in grouped_data:
                # Try fetching internship details once per code
                internship = Internships.query.filter_by(code=code).first()
                grouped_data[code] = {
                    "internship": {
                        "code": internship.code,
                        "title": internship.title,
                        "department": internship.department,
                        "location": internship.location,
                        "duration": internship.duration,
                        "stipend": internship.stipend,
                    },
                    "applicants": []
                }

            grouped_data[code]["applicants"].append({
                "fullname": app.fullname,
                "email": app.email,
                "resume_url": app.resume_url,
                "applied_on": app.applied_on.strftime("%Y-%m-%d %H:%M"),
                "internship_code": code
            })

        return jsonify(grouped_data), 200

    except Exception as e:
        print(f"[ERROR] Failed to fetch applicants: {e}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500
