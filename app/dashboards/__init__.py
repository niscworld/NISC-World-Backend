from .routes import Dashboards as Dashboard_routes
from .api import api as api_routes

from .Developer import Developer_routes
from .Hr import Hr_routes
from .Owner import owner_routes

Dashboard_routes.register_blueprint(api_routes, url_prefix='/api')

Dashboard_routes.register_blueprint(Developer_routes, url_prefix='/developer')
Dashboard_routes.register_blueprint(Hr_routes, url_prefix='/hr')
Dashboard_routes.register_blueprint(owner_routes, url_prefix='/owner')