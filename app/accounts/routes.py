from flask import Blueprint

Accounts = Blueprint('Accounts', __name__, template_folder="./templates", static_folder="./static")
