from flask_restx import fields, Namespace

# Define the input model for the API
def get_url_model(scan_ns: Namespace):
    return scan_ns.model('URL', {
        'url': fields.String(required=True, description='The URL to be scanned')
    })


# Define the output model for the API
def get_scan_result_model(scan_ns: Namespace):
    return scan_ns.model('ScanResult', {
        'original_url': fields.String(description='The original URL provided by the user'),
        'message': fields.String(description='A message about the scan result')
    })


def get_stats_model(scan_ns: Namespace):
    return scan_ns.model('Stats', {
        'harmless': fields.Integer(description='Number of harmless detections'),
        'malicious': fields.Integer(description='Number of malicious detections'),
        'suspicious': fields.Integer(description='Number of suspicious detections'),
        'timeout': fields.Integer(description='Number of timeouts'),
        'undetected': fields.Integer(description='Number of undetected detections')
    })


def get_report_model(scan_ns: Namespace):
    stats_model = get_stats_model(scan_ns)
    return scan_ns.model('Report', {
        'id': fields.String(description='Unique identifier for the result'),
        'stats': fields.Nested(stats_model, description='Scan statistics'),
        'status': fields.String(description='Status of the analysis'),
        'type': fields.String(description='Type of the analysis'),
        'url': fields.String(description='URL that was analyzed')
    })


def get_report_list_model(scan_ns: Namespace):
    report_model = get_report_model(scan_ns)
    return scan_ns.model('ReportList', {
        'reports': fields.List(fields.Nested(report_model), description='List of reports')
    })
