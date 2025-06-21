from .routes import Developer as Developer_routes

from .api import api as api_routes

Developer_routes.register_blueprint(api_routes, url_prefix='/api')
