from flask import Blueprint

Developer = Blueprint('Developer', __name__, template_folder="./templates", static_folder="./static")
