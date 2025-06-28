from .routes import owner as owner_routes

from .api import api as api_routes

owner_routes.register_blueprint(api_routes, url_prefix='/api')
