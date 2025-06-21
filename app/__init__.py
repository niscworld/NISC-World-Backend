from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/*": {"origins": "*"}})  # For dev only — change '*' to allowed origin in production
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)  # << add this

    from .routes import app as app_routes
    from .api import api_route
    from .accounts import Account_routes
    from .dashboards import Dashboard_routes
    from .internships import Internship_routes

    app.register_blueprint(app_routes, url_prefix='/')
    app.register_blueprint(api_route, url_prefix='/api')
    app.register_blueprint(Account_routes, url_prefix='/accounts')
    app.register_blueprint(Dashboard_routes, url_prefix='/dashboard')
    app.register_blueprint(Internship_routes, url_prefix='/internships')


    @app.before_request
    def call_frequent_function():
        from .utils import frequentCallerFunction
        frequentCallerFunction(app)

    return app
