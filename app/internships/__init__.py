from .routes import Internships as Internship_routes
from .api import api as api_routes


Internship_routes.register_blueprint(api_routes, url_prefix='/api')