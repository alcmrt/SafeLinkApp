from flask import Flask
from flask_restx import Api
from .controllers.scan_controller import scan_ns  # Import the Namespace, not the Blueprint
from .config.logging_config import setup_logging

def create_app():
    app = Flask(__name__)

    # set up logging by calling the function from the logging config module
    setup_logging(app)

    # Initialize Flask-RESTx and set up Swagger UI
    api = Api(
        app,
        version='1.0',
        title='SafeLinkApp API with Swagger',
        description='A simple Flask API with Swagger documentation',
        doc='/swagger-ui'  # Swagger UI will be available at /swagger-ui
    )

    # Add the Namespace directly to the main API
    api.add_namespace(scan_ns)  # Add the Namespace, not the Blueprint

    return app
