from flask import Flask
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
import os

# db = SQLAlchemy()
# migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # For dev only — change '*' to allowed origin in production
    # app.config.from_object('config.Config')
    # app.config.from_pyfile('config.py', silent=True)

    # db.init_app(app)
    # migrate.init_app(app, db)  # << add this

    from .api import api_route

    app.register_blueprint(api_route, url_prefix='/api')

    return app
