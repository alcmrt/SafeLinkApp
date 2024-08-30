from ..exceptions.custom_ssl_exception import CustomSSLError
from flask import Blueprint, request, jsonify
from flask_restx import Namespace, Api, Resource, fields  # Ensure Api is imported
from ..services.scan_service import scan_url_service
from ..services.extract_urls import extract_urls
from ..services.scan_service import submit_url_to_virustotal
from ..models.api_models import get_scan_result_model, get_url_model, get_report_list_model


# Creating a Namespace instead of a standalone Api
scan_ns = Namespace('scan', description='Scan Operations')

# Import and assign the models from the modules
url_model = get_url_model(scan_ns)
scan_result_model = get_scan_result_model(scan_ns)

# Get the dictionary containing the report_list_model
report_list_model = get_report_list_model(scan_ns)

# Define the output model for the API
'''scan_result_model = scan_ns.model('ScanResult', {
    'original_url': fields.String(description='The original URL provided by the user'),
    'message': fields.String(description='A message about the scan result')
})'''

# Define the input model for the API
'''url_model = scan_ns.model('URL', {
    'url': fields.String(required=True, description='The URL to be scanned')
})'''

@scan_ns.route('/url')
class ScanURL(Resource):

    @scan_ns.expect(url_model)  # Expect the input model for POST requests
    @scan_ns.response(200, 'Success', report_list_model)  # Define response model
    def post(self):
        """Scan a URL and return the result"""
        
        data = request.json

        try:
            result = submit_url_to_virustotal(data.get('url'))
            wrapped_result = {"reports": result}
            return jsonify(wrapped_result)
            
        except CustomSSLError as e:
            response = jsonify({'error': 'Bad Request', 'message': str(e)})
            response.status_code = 400
            return response
        except Exception as e:
            response = jsonify({'error': 'Internal Server Error', 'message': str(e)})
            response.status_code = 500
            return response

    def get(self):
        """Return a message for GET requests"""
        return jsonify({"message": "This is a GET request"})

# Now create a Blueprint and add the Namespace to it
scan_blueprint = Blueprint('scan', __name__)
api = Api(scan_blueprint)  # Add the Api instance to the Blueprint
api.add_namespace(scan_ns)  # Add the Namespace to the Api
