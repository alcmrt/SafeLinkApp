import requests
import base64
import time

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from flask import current_app


from ..services.extract_urls import extract_urls

# Your VirusTotal API key
API_KEY = ''

# VirusTotal endpoints
SCAN_URL = 'https://www.virustotal.com/api/v3/urls'
REPORT_URL = 'https://www.virustotal.com/api/v3/analyses/'


# Function to create a session with retry logic
def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

def encode_url(url):
    """Encode the URL in the format VirusTotal requires."""
    return base64.urlsafe_b64encode(url.encode()).decode().strip('=')

def submit_url_to_virustotal(url: str) -> list:
    """Submit a URL for scanning."""
    headers = {
        "x-apikey": API_KEY,
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }

    current_app.logger.info("Extracting all urls.")
    # extract all urls from given url address
    url_list = extract_urls(url)
    current_app.logger.info("URL count:{}".format(len(url_list)))


    # reports for all url addresses
    scanned_urls = []
    scanned_url_count = 0

    for url in url_list:
        # Encode the URL to meet VirusTotal's requirement
        data = {'url': url}
        
        try:
            response = requests_retry_session().post(SCAN_URL, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                scan_id = response.json()['data']['id'] 
                scanned_urls.append(get_scan_report(scan_id)) 
            else:
                scanned_urls.append({"url": url, "status": "incompleted"})

        except ConnectionError as e:
            current_app.logger.info("Connection error:{}".format(e))
            scanned_urls.append({"url": url, "status": "incompleted"})
        except requests.exceptions.RequestException as e:
            current_app.logger.info("Failed to fetch URL:{}".format(e))
            scanned_urls.append({"url": url, "status": "incompleted"})
        except Exception as e:
            current_app.logger.info("Failed to fetch URL:{}".format(e))
            scanned_urls.append({"url": url, "status": "incompleted"})

        scanned_url_count += 1

        current_app.logger.info("{} url(s) are scanned.".format(scanned_url_count))
        
        if len(url_list) > 3:
            # Wait for 15 seconds before the next request to avoid rate limiting
            current_app.logger.info("sleeping 15 seconds...")
            time.sleep(15)
    
    return scanned_urls


def get_scan_report(scan_id):
    """Retrieve the report for a submitted URL."""
    
    headers = {
        'x-apikey': API_KEY,
        "accept": "application/json"
    }

    report_summary = {}

    # Polling loop
    while True:
        response = requests.get(REPORT_URL + scan_id, headers=headers)
        
        if response.status_code == 200:
            report = response.json()
            status = report["data"]["attributes"]["status"]
            url =  report["meta"]["url_info"]["url"]

            if status == "queued":
                current_app.logger.info("Analysis is still queued. Waiting 10 seconds")
            
            elif status == "in-progress":
                current_app.logger.info("Analysis is in progress. Waiting 10 seconds")

            elif status == "completed":
                current_app.logger.info("Analysis completed for {}".format(url))
                
                report_summary["stats"] = report["data"]["attributes"]["stats"]
                report_summary["status"] = status
                report_summary["type"] = report["data"]["type"]
                report_summary["stats"] = report["data"]["attributes"]["stats"]
                report_summary["url"] = url
                report_summary["id"] = scan_id
                break

            time.sleep(10)
        
        else:
            break

    return report_summary


def scan_url_service(url):
    # Implement your scanning logic here
    # For now, just return a mock response
    return {'original_url': url, 'message': 'URL received successfully'}