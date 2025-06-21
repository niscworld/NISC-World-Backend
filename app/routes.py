from flask import Blueprint

app = Blueprint("app", __name__)

@app.route("/")
def home():
    return """
    <h1>Welcome to NAKSH INNOVATIVE SOLUTIONS CONSULTANCY</h1>
    <p>Visit our website: <a href='https://www.nisc.co.in' target='_blank'>nisc.co.in</a></p>
    """

# This will catch any undefined routes if registered at app level
@app.app_errorhandler(404)
def page_not_found(e):
    return "404 - Page Not Found", 404
