from flask import Blueprint

Dashboards = Blueprint('Dashboards', __name__, template_folder="./templates", static_folder="./static")
