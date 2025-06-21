from .routes import Dashboards as Dashboard_routes
from .api import api as api_routes

from .Developer import Developer_routes

Dashboard_routes.register_blueprint(api_routes, url_prefix='/api')

Dashboard_routes.register_blueprint(Developer_routes, url_prefix='/developer')