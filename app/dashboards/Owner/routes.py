from flask import Blueprint

owner = Blueprint('owner', __name__, template_folder="./templates", static_folder="./static")
