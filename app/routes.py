from flask import Blueprint, jsonify

app = Blueprint("app", __name__)

@app.route("/")
def home():
    def create_user():
        from app.models import db, User, Profile
        password = 'Srinu'
        fullname = 'SrinivasCharanK'
        email = 'sunkush.koppolu@gmail.com'
        position = 'Developer'

        if not all([password, fullname, position]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Generate user_id from role
        user_id = 'SrinivasCharanK'

        # Check if user_id or email already exists
        if User.query.get(user_id):
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
    def create_UserNameGenerationSequence():
        from app.models import db, UserNameGenerationSequence
        sequences = [
            UserNameGenerationSequence(type='A', year=25, current_users=0, next_user_number=1, total_users=0),
            UserNameGenerationSequence(type='E', year=25, current_users=0, next_user_number=1, total_users=0),
            UserNameGenerationSequence(type='I', year=25, current_users=0, next_user_number=1, total_users=0),
            UserNameGenerationSequence(type='O', year=25, current_users=0, next_user_number=1, total_users=0),
            UserNameGenerationSequence(type='U', year=25, current_users=0, next_user_number=1, total_users=0),
        ]

        db.session.add_all(sequences)
        db.session.commit()


    return """
    <h1>Welcome to NAKSH INNOVATIVE SOLUTIONS CONSULTANCY</h1>
    <p>Visit our website: <a href='https://www.nisc.co.in' target='_blank'>nisc.co.in</a></p>
    """


@app.route("/is_server_on")
def is_server_on():
    return jsonify(success=True)

# This will catch any undefined routes if registered at app level
@app.app_errorhandler(404)
def page_not_found(e):
    return "404 - Page Not Found", 404
