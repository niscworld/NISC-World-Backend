from flask import Blueprint

app = Blueprint("app", __name__)

def createUser():
    # Create User
    from .models import User, Profile, db
    from .utils import get_current_time
    user = User(user_id='SrinivasCharanK')
    user.set_password('Srinivas')  # Replace with actual password
    user.login_time = get_current_time()

    # Create Profile
    profile = Profile(
        user_id='SrinivasCharanK',
        fullname='Srinivas Charan K',
        email='charan@example.com',
        position='Developer'
    )

    # Add to DB
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()

    print("✅ User created successfully!")

@app.route("/")
def home():
    createUser()
    return """
    <h1>Welcome to NAKSH INNOVATIVE SOLUTIONS CONSULTANCY</h1>
    <p>Visit our website: <a href='https://www.nisc.co.in' target='_blank'>nisc.co.in</a></p>
    """

# This will catch any undefined routes if registered at app level
@app.app_errorhandler(404)
def page_not_found(e):
    return "404 - Page Not Found", 404
