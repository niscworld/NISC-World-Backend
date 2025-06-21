from .routes import Accounts as Account_routes

from .api import api as api_routes

Account_routes.register_blueprint(api_routes, url_prefix='/api')
