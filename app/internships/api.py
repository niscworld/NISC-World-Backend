from flask import Blueprint, jsonify, request
from app.models import Internships

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
