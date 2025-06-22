from .routes import Hr as Hr_routes

from .api import api as api_routes

Hr_routes.register_blueprint(api_routes, url_prefix='/api')
