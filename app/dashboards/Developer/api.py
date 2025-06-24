from flask import Blueprint, jsonify, request
from app.models import db, User, Profile
from app.util_models import create_internship
from app.util_wraps import verify_dashboard_access

api = Blueprint("api", __name__)

@api.route('/view-users', methods=["POST"])
@verify_dashboard_access
def view_users():
    profiles = Profile.query.all()

    users_data = []
    for profile in profiles:
        users_data.append({
            'user_id': profile.user_id,
            'fullname': profile.fullname,
            'email': profile.email,
            'position': profile.position,
        })

    return jsonify(users_data), 200


@api.route('/create-user', methods=["POST"])
@verify_dashboard_access
def create_user():
    data = request.get_json()
    password = data.get('password')
    fullname = data.get('fullname')
    email = data.get('email')
    position = data.get('position')

    if not all([password, fullname, position]):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # Generate user_id from role
        from app.utils import generate_username
        user_id = generate_username(position)
        if not user_id:
            return jsonify({'message': 'Unable to generate username'}), 500

        # Check if user_id or email already exists
        if User.query.get(user_id) or (email and User.query.filter_by(email=email).first()):
            return jsonify({'message': 'User ID or Email already exists'}), 409

        new_user = User(user_id=user_id, is_active=True)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        new_profile = Profile(
            user_id=user_id,
            fullname=fullname,
            email=email,
            position=position
        )
        db.session.add(new_profile)
        db.session.commit()

        return jsonify({'message': 'User created successfully', 'user_id': user_id, 'password': password}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500



@api.route('/create-internship', methods=['POST'])
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