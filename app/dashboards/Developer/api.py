from flask import Blueprint, jsonify, request
from app.models import db, User, Profile
from app.util_models import create_internship

api = Blueprint("api", __name__)

@api.route('/view-users', methods=["POST"])
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
def create_user():
    data = request.get_json()
    print(data)
    user_id = data.get('user_id')
    password = data.get('password')
    fullname = data.get('fullname')
    email = data.get('email')
    position = data.get('position')

    if not all([user_id, password, fullname, position]):
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.get(user_id):
        return jsonify({'message': 'User ID or Email already exists'}), 409

    try:
        new_user = User(user_id=user_id)
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

        return jsonify({'message': 'User created successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@api.route('/create-internship', methods=['POST'])
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